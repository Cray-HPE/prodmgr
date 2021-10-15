"""
Unit tests for prodmgr.

(C) Copyright 2021 Hewlett Packard Enterprise Development LP.
"""

from argparse import Namespace
import unittest
from unittest.mock import patch

from tests.mocks import MOCK_PRODUCT_CATALOG_DATA

from prodmgr.main import get_install_utility_image, run_install_utility, ProdmgrError
from prodmgr.constants import (
    DEFAULT_CERT_SRC_DIR,
    DEFAULT_CERT_TARGET_DIR,
    DEFAULT_CONTAINER_REGISTRY_HOSTNAME,
    DEFAULT_KUBE_CONFIG_SRC_FILE,
    DEFAULT_KUBE_CONFIG_TARGET_FILE,
    DEFAULT_PRODUCT_CATALOG_NAME,
    DEFAULT_PRODUCT_CATALOG_NAMESPACE
)


class TestGetInstallUtilityImage(unittest.TestCase):
    """Test the get_install_utility_image function."""

    def setUp(self):
        """Set up mocks."""
        self.mock_k8s_api = patch('prodmgr.main.CoreV1Api').start().return_value
        self.mock_load_config = patch('prodmgr.main.load_kube_config').start()
        self.mock_k8s_api.read_namespaced_config_map.return_value.data = MOCK_PRODUCT_CATALOG_DATA

    def tearDown(self):
        """Stop patches."""
        patch.stopall()

    def test_get_install_utility_image(self):
        """Test getting the install utility image from the product catalog."""
        expected_image = 'cray/sat-install-utility', '1.4.0'
        actual_image = get_install_utility_image(
            'sat', '1.0.0', DEFAULT_PRODUCT_CATALOG_NAME, DEFAULT_PRODUCT_CATALOG_NAMESPACE
        )
        self.mock_k8s_api.read_namespaced_config_map.assert_called_once_with(
            DEFAULT_PRODUCT_CATALOG_NAME, DEFAULT_PRODUCT_CATALOG_NAMESPACE
        )
        self.mock_load_config.assert_called_once_with()
        self.assertEqual(expected_image, actual_image)

    def test_get_install_utility_image_unknown_product(self):
        """Test getting an install utility image from the product catalog with an unknown product."""
        with self.assertRaisesRegex(ProdmgrError, f'No product information found for doesNotExist:1.0.0'):
            get_install_utility_image(
                'doesNotExist', '1.0.0', DEFAULT_PRODUCT_CATALOG_NAME, DEFAULT_PRODUCT_CATALOG_NAMESPACE
            )

    def test_get_install_utility_image_unknown_version(self):
        """Test getting an install utility image from the product catalog with an unknown version."""
        with self.assertRaisesRegex(ProdmgrError, f'No product information found for sat:1.0.2'):
            get_install_utility_image(
                'sat', '1.0.2', DEFAULT_PRODUCT_CATALOG_NAME, DEFAULT_PRODUCT_CATALOG_NAMESPACE
            )

    def test_get_install_utility_custom_config_map_name_namespace(self):
        """Test getting an install utility image with a custom config map name and namespace"""
        with self.assertRaisesRegex(ProdmgrError, f'No product information found for sat:1.0.2'):
            get_install_utility_image(
                'sat', '1.0.2', 'another-cray-product-catalog', 'more-services'
            )
        self.mock_k8s_api.read_namespaced_config_map.assert_called_once_with(
            'another-cray-product-catalog', 'more-services'
        )


class TestRunInstallUtility(unittest.TestCase):
    """Test the run_install_utility function."""

    def setUp(self):
        """Set up mocks."""
        self.image_name = 'cray/sat-install-utility'
        self.image_version = '1.0.1'
        self.args = Namespace(
            action='activate',
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
        self.mock_check_call = patch('prodmgr.main.subprocess.check_call').start()

    def tearDown(self):
        """Stop patches."""
        patch.stopall()

    def test_run_install_utility_default(self):
        """Test running run_install_utility with default arguments."""
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


if __name__ == '__main__':
    unittest.main()
