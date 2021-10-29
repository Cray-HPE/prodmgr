"""
CLI argument parser for prodmgr.

Copyright 2021 Hewlett Packard Enterprise Development LP.
"""

import argparse

from prodmgr.constants import (
    DEFAULT_CONTAINER_REGISTRY_HOSTNAME,
    DEFAULT_CERT_SRC_DIR,
    DEFAULT_CERT_TARGET_DIR,
    DEFAULT_PRODUCT_CATALOG_NAME,
    DEFAULT_PRODUCT_CATALOG_NAMESPACE,
    DEFAULT_KUBE_CONFIG_SRC_FILE,
    DEFAULT_KUBE_CONFIG_TARGET_FILE
)


def create_parser():
    """Create an argument parser for this command.

    Returns:
        argparse.ArgumentParser: The parser.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['uninstall', 'activate'],
        help='Specify the operation to execute on a product.'
    )
    parser.add_argument(
        'product',
        help='The name of the product to uninstall or activate.'
    )
    parser.add_argument(
        'version',
        help='Specify the version of the product to operate on.'
    )
    # These arguments need a default value because this script
    # looks in the product catalog for the install utility image version
    parser.add_argument(
        '--product-catalog-name',
        help='The name of the product catalog Kubernetes ConfigMap',
        default=DEFAULT_PRODUCT_CATALOG_NAME
    )
    parser.add_argument(
        '--product-catalog-namespace',
        help='The namespace of the product catalog Kubernetes ConfigMap',
        default=DEFAULT_PRODUCT_CATALOG_NAMESPACE
    )
    # Arguments that only apply to this script
    parser.add_argument(
        '--kube-config-src-file',
        help='The location of the kubernetes configuration file on the host',
        default=DEFAULT_KUBE_CONFIG_SRC_FILE
    )
    parser.add_argument(
        '--kube-config-target-file',
        help='The location where the kubernetes configuration '
             'file should be mounted in the container',
        default=DEFAULT_KUBE_CONFIG_TARGET_FILE
    )
    parser.add_argument(
        '--cert-src-dir',
        help='The directory on the host containing trusted certificates',
        default=DEFAULT_CERT_SRC_DIR,
    )
    parser.add_argument(
        '--cert-target-dir',
        help='The directory where trusted certificates '
             'should be mounted in the container',
        default=DEFAULT_CERT_TARGET_DIR,
    )
    parser.add_argument(
        '--container-registry-hostname',
        help='The hostname of the container image registry',
        default=DEFAULT_CONTAINER_REGISTRY_HOSTNAME,
    )

    return parser
