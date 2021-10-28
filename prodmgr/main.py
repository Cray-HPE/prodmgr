"""
Main entry point for prodmgr.

Copyright 2021 Hewlett Packard Enterprise Development LP.
"""

import subprocess
import warnings

from kubernetes.config import load_kube_config, ConfigException
from kubernetes.client import CoreV1Api
from kubernetes.client.rest import ApiException
from urllib3.exceptions import MaxRetryError
from yaml import safe_load, YAMLLoadWarning, YAMLError


from prodmgr.parser import create_parser


class ProdmgrError(Exception):
    """Something failed in the prodmgr script."""
    pass


def get_k8s_api():
    """Load a Kubernetes CoreV1Api and return it.

    Returns:
        CoreV1Api: The Kubernetes API.

    Raises:
        ProductInstallException: if there was an error loading the
            Kubernetes configuration.
    """
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', category=YAMLLoadWarning)
            load_kube_config()
        return CoreV1Api()
    except ConfigException as err:
        print(err)
        raise SystemExit(1)


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
    k8s_client = get_k8s_api()
    try:
        config_map = k8s_client.read_namespaced_config_map(product_catalog_name, product_catalog_namespace)
    except MaxRetryError as err:
        raise ProdmgrError(
            f'Unable to connect to Kubernetes to read '
            f'{product_catalog_namespace}/{product_catalog_name} ConfigMap: {err}'
        )
    except ApiException as err:
        # The full string representation of ApiException is very long, so just log err.reason.
        raise ProdmgrError(f'Error reading {product_catalog_namespace}/{product_catalog_name} ConfigMap: {err.reason}')

    if config_map.data is None:
        raise ProdmgrError(f'No data found in {product_catalog_namespace}/{product_catalog_name} ConfigMap.')

    try:
        return {
            product_name: safe_load(product_versions)
            for product_name, product_versions in config_map.data.items()
        }
    except YAMLError as err:
        raise ProdmgrError(f'Failed to load ConfigMap data: {err}')


def get_install_utility_image(product, version, product_catalog_name, product_catalog_namespace):
    """Use config map data to get the right version of the install utility to use.

    Args:
        product (str): The name of the product for which to get the install
            utility image version.
        version (str): The version of the product for which to get the install
            utility image version.
        product_catalog_name (str): The name of the Kubernetes config map
            containing the product catalog.
        product_catalog_namespace (str): The namespace of the Kubernetes config
            map containing the product catalog.

    Returns:
        tuple: A tuple of:
            - (str): Install utility image name
            - (str): Install utility image version
    """
    installed_products = read_catalog(product_catalog_name, product_catalog_namespace)
    install_utility_image_name = f'cray/{product}-install-utility'
    product_data = installed_products.get(product, {}).get(version, {})

    if not product_data:
        raise ProdmgrError(f'No product information found for {product}:{version}.')

    component_versions = product_data.get('component_versions', {})

    install_utility_images = [img for img in component_versions.get('docker', [])
                              if img.get('name') == install_utility_image_name]

    if not install_utility_images:
        raise ProdmgrError(
            f'Image {install_utility_image_name} not found in product data for {product}:{version}'
        )

    elif len(install_utility_images) > 1:
        raise ProdmgrError(
            f'Multiple {install_utility_image_name} images found in product data for {product}:{version}'
        )

    image_version = install_utility_images[0].get('version')
    if not image_version:
        raise ProdmgrError(
            f'Unable to determine version of image {install_utility_image_name} from product data'
        )

    return install_utility_image_name, image_version


def run_install_utility(image_name, image_version, args, remaining_args):
    """Invoke the install utility container.

    Args:
        image_name (str): The name of the image to run.
        image_version (str): The version of the image to run.
        args (Namespace): The argparse.Namespace object containing
            command-line arguments passed to the command.
        remaining_args (list): List of remaining command-line arguments
            not parsed by parse_known_args().
    """
    print(f'Running {image_name}:{image_version}')

    podman_command = [
        'podman', 'run', '--rm',
        '--mount', f'type=bind,src={args.kube_config_src_file},target={args.kube_config_target_file},ro=true',
        '--mount', f'type=bind,src={args.cert_src_dir},target={args.cert_target_dir},ro=true',
        f'{args.container_registry_hostname}/{image_name}:{image_version}',
        args.action, args.version,
        # --product-catalog-name and --product-catalog-namespace are used both by this
        # script as well as with the underlying install utility image.
        f'--product-catalog-name={args.product_catalog_name}',
        f'--product-catalog-namespace={args.product_catalog_namespace}'
    ]

    # Pass any unrecognized CLI arguments to the container
    podman_command.extend(remaining_args)

    try:
        subprocess.check_call(podman_command)
    except subprocess.CalledProcessError as cpe:
        raise ProdmgrError(f'Running install utility failed: {cpe}')


def main():
    """Main method."""
    parser = create_parser()
    # Parse arguments that are known to the script, but other arguments
    # are assumed to belong to the underlying container script.
    args, remaining_args = parser.parse_known_args()
    try:
        install_utility_image_name, install_utility_image_version = get_install_utility_image(
            args.product, args.version, args.product_catalog_name, args.product_catalog_namespace
        )
        run_install_utility(install_utility_image_name, install_utility_image_version, args, remaining_args)
    except ProdmgrError as err:
        print(err)
        raise SystemExit(1)
