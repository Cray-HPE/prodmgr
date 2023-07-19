#
# MIT License
#
# (C) Copyright 2021-2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
"""
Main entry point for prodmgr.
"""
import os
import logging
import sys

from subprocess import check_call, check_output, CalledProcessError, STDOUT
from yaml import safe_load, YAMLError
from prodmgr.parser import create_parser
from datetime import datetime
from prodmgr.constants import DEFAULT_LOG_DIR

LOGGER = logging.getLogger('prodmgr')
logfile = ''


class ProdmgrError(Exception):
    """Something failed in the prodmgr script."""
    pass


def _setup_logging(product, version, action):
    """ Setup stdout logging for this script """
    LOGGER.setLevel(logging.DEBUG)
    global logfile

    # set the console logger
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s')
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    LOGGER.addHandler(console_handler)

    # set the file logger
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logfile = f'{action}-{product}-{version}-' + timestamp

    if not os.path.exists(DEFAULT_LOG_DIR):
        try:
            os.makedirs(DEFAULT_LOG_DIR)
            logfile = os.path.join(DEFAULT_LOG_DIR, logfile)
        except OSError as error:
            LOGGER.debug(f"Using current directory {os.getcwd()} for log file")
            logfile = os.path.join(os.getcwd(), logfile)
    else:
        logfile = os.path.join(DEFAULT_LOG_DIR, logfile)

    file_handler = logging.FileHandler(filename=logfile)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # noqa: E501
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    LOGGER.addHandler(file_handler)


def read_catalog(product_catalog_name, product_catalog_namespace):
    """Read the product catalog and return data for each product version.

    Args:
        product_catalog_name (str): The name of the Kubernetes config map
            containing the product catalog.
        product_catalog_namespace (str): The namespace of the Kubernetes config
            map containing the product catalog.

    Returns:
        dict: A dictionary of product names to dictionaries of version numbers
            to sub-component data.
    """
    config_map_name = f'ConfigMap {product_catalog_namespace}/{product_catalog_name}'
    try:
        config_map = safe_load(check_output([
            'kubectl', 'get', 'configmap', f'--namespace={product_catalog_namespace}',
            product_catalog_name, '--output=yaml'
        ]).decode())
    except CalledProcessError as err:
        raise ProdmgrError(
            f'Unable to to read {config_map_name}: {err}'
        )
    except YAMLError as err:
        raise ProdmgrError(
            f'Failed to load data from {config_map_name}: {err}')

    if not config_map.get('data'):
        raise ProdmgrError(f'{config_map_name} has no data under "data" key')

    try:
        return {
            product_name: safe_load(product_versions)
            for product_name, product_versions in config_map['data'].items()
        }
    except YAMLError as err:
        raise ProdmgrError(
            f'A product entry in {config_map_name} contained invalid YAML: {err}'
        )


def get_docker_image(docker_image, product, version, product_catalog_name, product_catalog_namespace,
                     base_name_match=True):
    """Find the version of the name Docker image for the specified product and version in the config map.

    Args:
        docker_image (str): The name of the Docker image for which to get the version
        product (str): The name of the product for which to get the Docker image's version
        version (str): The version of the product for which to get the Docker image's version
        product_catalog_name (str): The name of the Kubernetes config map
            containing the product catalog.
        product_catalog_namespace (str): The namespace of the Kubernetes config
            map containing the product catalog.
        base_name_match (bool): this flag, if set to True, means only the base
            name portion the string (i.e. the file name) retrieved from the
            product catalog will be matched against the docker_image.
            If set to False, it means the entire string including any path
            elements that precede the file name will be part of the match.
            Example:
              String from product catalog is '/path/file-name'
              base_name_match=True --> docker_image matched against 'base-name'
              base_name_match=False --> docker_image matched against '/path/base-name'

    Returns:
        tuple: A tuple of:
            - (str): Docker image name
            - (str): Docker image version

    Raises:
        ProdmgrError when an image is not found
    """
    installed_products = read_catalog(
        product_catalog_name, product_catalog_namespace)
    product_data = installed_products.get(product, {}).get(version, {})

    if not product_data:
        raise ProdmgrError(
            f'No product information found for {product}:{version}.')

    component_versions = product_data.get('component_versions', {})
    if not component_versions:
        raise ProdmgrError(
            f'No component information found for {product}:{version}.')

    if base_name_match:
        if '/' in docker_image:
            raise ProdmgrError(f'{docker_image} contains an invalid character: /. '
                               f'For full path search, set base_name_match to False.')

        docker_images = [img for img in component_versions.get('docker', [])
                         if os.path.basename(img.get('name')) == docker_image]
    else:
        docker_images = [img for img in component_versions.get('docker', [])
                         if img.get('name') == docker_image]

    if not docker_images:
        raise ProdmgrError(
            f'Image {docker_image} not found in product data for {product}:{version}'
        )

    elif len(docker_images) > 1:
        raise ProdmgrError(
            f'Multiple {docker_image} images found in product data for {product}:{version}'
        )

    image_name = docker_images[0].get('name')
    if not image_name:
        raise ProdmgrError(
            f'Unable to determine name of image {docker_image} from product data'
        )

    image_version = docker_images[0].get('version', None)
    if not image_version:
        raise ProdmgrError(
            f'Unable to determine version of image {docker_image} from product data'
        )

    return image_name, image_version


def run_deletion_utility(image_name, image_version, args, remaining_args):
    """Invoke the Docker image container.

    Args:
        image_name (str): The name of the image to run.
        image_version (str): The version of the image to run.
        args (Namespace): The argparse.Namespace object containing
            command-line arguments passed to the command.
        remaining_args (list): List of remaining command-line arguments
            not parsed by parse_known_args().
    """
    LOGGER.debug(f'Running {image_name}:{image_version}')

    podman_command = [
        'podman', 'run', '--rm',
        '--mount', f'type=bind,src={args.kube_config_src_file},target={args.kube_config_target_file},ro=true',
        '--mount', f'type=bind,src={args.cert_src_dir},target={args.cert_target_dir},ro=true',
        '--mount', f'type=bind,src={DEFAULT_LOG_DIR},target={DEFAULT_LOG_DIR},ro=false']

    if args.extra_podman_config:
        podman_command = podman_command + args.extra_podman_config.split(" ")

    container_command = [f'{args.container_registry_hostname}/{image_name}:{image_version}',
                         args.action, args.product, args.version,
                         # --product-catalog-name and --product-catalog-namespace are used both by this
                         # script as well as with the underlying install utility image.
                         f'--product-catalog-name={args.product_catalog_name}',
                         f'--product-catalog-namespace={args.product_catalog_namespace}',
                         f'--log-file={logfile}',
                         f'--dry-run={args.dry_run}'
                         ]
    deletion_utility_command = podman_command + container_command

    # Pass any unrecognized CLI arguments to the container
    deletion_utility_command.extend(remaining_args)
    LOGGER.debug(
        f"Launching deletion utility using - {deletion_utility_command}")

    try:
        check_call(
            deletion_utility_command, universal_newlines=True, stderr=STDOUT)
    except CalledProcessError as cpe:
        raise ProdmgrError(f'Running {image_name} failed: {cpe}')


def run_install_utility(image_name, image_version, args, remaining_args):
    """Invoke the Docker image container.

    Args:
        image_name (str): The name of the image to run.
        image_version (str): The version of the image to run.
        args (Namespace): The argparse.Namespace object containing
            command-line arguments passed to the command.
        remaining_args (list): List of remaining command-line arguments
            not parsed by parse_known_args().
    """
    LOGGER.debug(f'Running {image_name}:{image_version}')

    podman_command = [
        'podman', 'run', '--rm',
        '--mount', f'type=bind,src={args.kube_config_src_file},target={args.kube_config_target_file},ro=true',
        '--mount', f'type=bind,src={args.cert_src_dir},target={args.cert_target_dir},ro=true']

    if args.extra_podman_config:
        podman_command = podman_command + args.extra_podman_config.split(" ")

    container_command = [f'{args.container_registry_hostname}/{image_name}:{image_version}',
                         args.action, args.version,
                         # --product-catalog-name and --product-catalog-namespace are used both by this
                         # script as well as with the underlying install utility image.
                         f'--product-catalog-name={args.product_catalog_name}',
                         f'--product-catalog-namespace={args.product_catalog_namespace}'
                         ]
    install_utility_command = podman_command + container_command

    # Pass any unrecognized CLI arguments to the container
    install_utility_command.extend(remaining_args)
    LOGGER.debug(
        f"Launching install utility using - {install_utility_command}")

    try:
        install_result = check_output(
            install_utility_command, universal_newlines=True, stderr=STDOUT)
    except CalledProcessError as cpe:
        LOGGER.error(cpe.output)
        raise ProdmgrError(f'Running {image_name} failed: {cpe}')
    else:
        LOGGER.info(install_result)


def main(*args):
    """Main method."""
    parser = create_parser()
    # Parse arguments that are known to the script, but other arguments
    # are assumed to belong to the underlying container script.
    args, remaining_args = parser.parse_known_args()
    _setup_logging(args.product, args.version, args.action.lower())
    try:
        if args.action.lower() == 'activate':
            LOGGER.warning('The "activate" action is deprecated.')
            docker_image_to_find = f'{args.product}-install-utility'
            # Find the image version.
            image_name, image_version = get_docker_image(docker_image_to_find,
                                                         args.product,
                                                         args.version,
                                                         args.product_catalog_name,
                                                         args.product_catalog_namespace)
            run_install_utility(image_name, image_version,
                                args, remaining_args)
        else:
            if args.action.lower() == 'uninstall':
                LOGGER.warning('The "uninstall" action is deprecated.')
            image_name = args.deletion_image_name
            image_version = args.deletion_image_version
            run_deletion_utility(image_name, image_version,
                                 args, remaining_args)
    except ProdmgrError as err:
        LOGGER.critical(err)
        raise SystemExit(1)


if "__main__" == __name__:
    main()
