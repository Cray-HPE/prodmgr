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
Unit tests for prodmgr.
"""

from argparse import Namespace
from subprocess import CalledProcessError
import unittest
from unittest.mock import patch

from yaml import safe_dump

from tests.mocks import MOCK_CONFIGMAP_OUTPUT

from prodmgr.main import get_docker_image, run_install_utility, run_deletion_utility, ProdmgrError
from prodmgr.constants import (
    DEFAULT_CERT_SRC_DIR,
    DEFAULT_CERT_TARGET_DIR,
    DEFAULT_CONTAINER_REGISTRY_HOSTNAME,
    DEFAULT_KUBE_CONFIG_SRC_FILE,
    DEFAULT_KUBE_CONFIG_TARGET_FILE,
    DEFAULT_PRODUCT_CATALOG_NAME,
    DEFAULT_PRODUCT_CATALOG_NAMESPACE
)


class TestGetDockerImage(unittest.TestCase):
    """Test the get_docker_image function."""

    def setUp(self):
        """Set up mocks."""
        self.mock_check_output = patch('prodmgr.main.check_output').start()
        self.mock_check_output.return_value.decode.return_value = MOCK_CONFIGMAP_OUTPUT

    def tearDown(self):
        """Stop patches."""
        patch.stopall()

    def test_get_docker_image_match_filename(self):
        """Test getting the docker image from the product catalog."""
        product = 'sat'
        version = '1.0.0'
        docker_image = 'sat-install-utility'
        expected_image = 'cray/sat-install-utility', '1.4.0'
        actual_image = get_docker_image(
            docker_image, product, version, DEFAULT_PRODUCT_CATALOG_NAME,
            DEFAULT_PRODUCT_CATALOG_NAMESPACE, True
        )
        self.mock_check_output.assert_called_once_with(
            ['kubectl', 'get', 'configmap', f'--namespace={DEFAULT_PRODUCT_CATALOG_NAMESPACE}',
             DEFAULT_PRODUCT_CATALOG_NAME, '--output=yaml']
        )
        self.assertEqual(expected_image, actual_image)

    def test_get_docker_image_match_path_and_filename(self):
        """Test getting the docker image from the product catalog."""
        product = 'sat'
        version = '1.0.0'
        docker_image = 'cray/sat-install-utility'
        expected_image = 'cray/sat-install-utility', '1.4.0'
        actual_image = get_docker_image(
            docker_image, product, version, DEFAULT_PRODUCT_CATALOG_NAME,
            DEFAULT_PRODUCT_CATALOG_NAMESPACE, False
        )
        self.mock_check_output.assert_called_once_with(
            ['kubectl', 'get', 'configmap', f'--namespace={DEFAULT_PRODUCT_CATALOG_NAMESPACE}',
             DEFAULT_PRODUCT_CATALOG_NAME, '--output=yaml']
        )
        self.assertEqual(expected_image, actual_image)

    def test_get_docker_image_match_filename_no_match(self):
        """Test not finding the docker image in the product catalog using the entire string as file name."""
        product = 'sat'
        version = '1.0.0'
        docker_image = 'cray/sat-install-utility'
        with self.assertRaisesRegex(ProdmgrError, f'{docker_image} contains an invalid character: /. For full path search, set file_name_match to False.'):
            get_docker_image(
                docker_image, product, version, DEFAULT_PRODUCT_CATALOG_NAME,
                DEFAULT_PRODUCT_CATALOG_NAMESPACE, True
            )

    def test_get_docker_image_match_path_and_filename_no_match(self):
        """Test not finding the docker image in the product catalog using just the file name but with the file_name_match set to False."""
        product = 'sat'
        version = '1.0.0'
        docker_image = 'sat-install-utility'
        with self.assertRaisesRegex(ProdmgrError, f'Image {docker_image} not found in product data for {product}:{version}'):
            get_docker_image(
                docker_image, product, version, DEFAULT_PRODUCT_CATALOG_NAME,
                DEFAULT_PRODUCT_CATALOG_NAMESPACE, False
            )

    def test_get_docker_image_unknown_product(self):
        """Test getting an install utility image from the product catalog with an unknown product."""
        with self.assertRaisesRegex(ProdmgrError, f'No product information found for doesNotExist:1.0.0'):
            get_docker_image(
                'sat-install-utility', 'doesNotExist', '1.0.0', DEFAULT_PRODUCT_CATALOG_NAME,
                DEFAULT_PRODUCT_CATALOG_NAMESPACE, True
            )

    def test_get_docker_image_command_failed(self):
        """Test when the command to read the product catalog failed."""
        self.mock_check_output.side_effect = CalledProcessError(returncode=1, cmd='kubectl')
        expected_err_regex = ('Unable to to read ConfigMap services/cray-product-catalog: '
                              'Command \'kubectl\' returned non-zero exit status 1.')
        with self.assertRaisesRegex(ProdmgrError, expected_err_regex):
            get_docker_image(
                'sat-install-utility', 'sat', '1.0.0', DEFAULT_PRODUCT_CATALOG_NAME,
                DEFAULT_PRODUCT_CATALOG_NAMESPACE, True
            )

    def test_get_docker_image_bad_yaml(self):
        """Test when the product catalog returned bad yaml."""
        # Use a tab character as an example of something that is invalid YAML
        self.mock_check_output.return_value.decode.return_value = '\t'
        with self.assertRaisesRegex(ProdmgrError, 'Failed to load data from ConfigMap services/cray-product-catalog'):
            get_docker_image(
                'sat-install-utility', 'sat', '1.0.0', DEFAULT_PRODUCT_CATALOG_NAME,
                DEFAULT_PRODUCT_CATALOG_NAMESPACE, True
            )

    def test_get_docker_image_bad_product_yaml(self):
        """Test when the product catalog returned bad yaml under a particular product."""
        expected_err_regex = 'A product entry in ConfigMap services/cray-product-catalog contained invalid YAML'
        # Use a tab character as an example of something that is invalid YAML
        self.mock_check_output.return_value.decode.return_value = safe_dump(
            {'data': {'sat': '\t'}}
        )
        with self.assertRaisesRegex(ProdmgrError, expected_err_regex):
            get_docker_image(
                'sat-install-utility', 'sat', '1.0.0', DEFAULT_PRODUCT_CATALOG_NAME,
                DEFAULT_PRODUCT_CATALOG_NAMESPACE, True
            )

    def test_get_docker_image_unknown_version(self):
        """Test getting an install utility image from the product catalog with an unknown version."""
        with self.assertRaisesRegex(ProdmgrError, f'No product information found for sat:1.0.2'):
            get_docker_image(
                'sat-install-utility', 'sat', '1.0.2', DEFAULT_PRODUCT_CATALOG_NAME,
                DEFAULT_PRODUCT_CATALOG_NAMESPACE, True
            )

    def test_get_install_utility_custom_config_map_name_namespace(self):
        """Test getting an install utility image with a custom config map name and namespace"""
        with self.assertRaisesRegex(ProdmgrError, f'No product information found for sat:1.0.2'):
            get_docker_image(
                'sat-install-utility', 'sat', '1.0.2',
                'another-cray-product-catalog', 'more-services', True
            )
        self.mock_check_output.assert_called_once_with(
            ['kubectl', 'get', 'configmap', '--namespace=more-services',
             'another-cray-product-catalog', '--output=yaml']
        )


class TestRunInstallUtility(unittest.TestCase):
    """Test the run_install_utility function."""

    def setUp(self):
        """Set up mocks."""
        self.image_name = 'No-Image'
        self.image_version = '6.6.6'
        self.args = Namespace(
            product='Unknown product',
            action='inactive',
            version='1.0.0',
            kube_config_src_file=DEFAULT_KUBE_CONFIG_SRC_FILE,
            kube_config_target_file=DEFAULT_KUBE_CONFIG_TARGET_FILE,
            cert_src_dir=DEFAULT_CERT_SRC_DIR,
            cert_target_dir=DEFAULT_CERT_TARGET_DIR,
            product_catalog_name=DEFAULT_PRODUCT_CATALOG_NAME,
            product_catalog_namespace=DEFAULT_PRODUCT_CATALOG_NAMESPACE,
            container_registry_hostname=DEFAULT_CONTAINER_REGISTRY_HOSTNAME
        )
        self.remaining_args = ['--additional-option']
        self.mock_check_call = patch('prodmgr.main.check_call').start()

    def tearDown(self):
        """Stop patches."""
        patch.stopall()

    def test_run_install_utility_default(self):
        """Test running run_install_utility with default arguments."""
        self.image_name = 'cray/sat-install-utility'
        self.image_version = '1.0.1'
        self.args.action = 'activate'
        expected_command = [
            'podman', 'run', '--rm',
            '--mount', f'type=bind,src={DEFAULT_KUBE_CONFIG_SRC_FILE},target={DEFAULT_KUBE_CONFIG_TARGET_FILE},ro=true',
            '--mount', f'type=bind,src={DEFAULT_CERT_SRC_DIR},target={DEFAULT_CERT_TARGET_DIR},ro=true',
            f'{DEFAULT_CONTAINER_REGISTRY_HOSTNAME}/{self.image_name}:{self.image_version}',
            'activate', '1.0.0',
            f'--product-catalog-name={DEFAULT_PRODUCT_CATALOG_NAME}',
            f'--product-catalog-namespace={DEFAULT_PRODUCT_CATALOG_NAMESPACE}',
            '--additional-option'
        ]
        run_install_utility(self.image_name, self.image_version, self.args, self.remaining_args)
        self.mock_check_call.assert_called_once_with(expected_command)

    def test_run_delete_utility_default(self):
        """Test running run_deletion_utility with default arguments."""
        self.image_name = 'product-delete-utility'
        self.image_version = '1.0.0'
        self.args.product = 'old-product'
        self.args.action = 'delete'

        expected_command = [
            'podman', 'run', '--rm',
            '--mount', f'type=bind,src={DEFAULT_KUBE_CONFIG_SRC_FILE},target={DEFAULT_KUBE_CONFIG_TARGET_FILE},ro=true',
            '--mount', f'type=bind,src={DEFAULT_CERT_SRC_DIR},target={DEFAULT_CERT_TARGET_DIR},ro=true',
            f'{DEFAULT_CONTAINER_REGISTRY_HOSTNAME}/{self.image_name}:{self.image_version}',
            self.args.action, self.args.product, self.image_version,
            f'--product-catalog-name={DEFAULT_PRODUCT_CATALOG_NAME}',
            f'--product-catalog-namespace={DEFAULT_PRODUCT_CATALOG_NAMESPACE}',
            '--additional-option'
        ]
        run_deletion_utility(self.image_name, self.image_version, self.args, self.remaining_args)
        self.mock_check_call.assert_called_once_with(expected_command)

if __name__ == '__main__':
    unittest.main()
