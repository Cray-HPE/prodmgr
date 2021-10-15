"""
Constant values for prodmgr.

Copyright 2021 Hewlett Packard Enterprise Development LP.
"""


import os

# TODO(CRAYSAT-898): Update this for CSM 1.2 and 1.3 DNS name changes
DEFAULT_CONTAINER_REGISTRY_HOSTNAME = 'registry.local'
DEFAULT_KUBE_CONFIG_SRC_FILE = '/etc/kubernetes/admin.conf'
DEFAULT_KUBE_CONFIG_TARGET_FILE = f'{os.getenv("HOME")}/.kube/config'
DEFAULT_CERT_SRC_DIR = '/etc/pki/trust/anchors'
DEFAULT_CERT_TARGET_DIR = '/usr/local/share/ca-certificates'
# TODO: it would be nice to not have to define these default values twice:
#    once here and once in shasta_install_utility_common.constants. I am not
#    sure how, though.
DEFAULT_PRODUCT_CATALOG_NAME = 'cray-product-catalog'
DEFAULT_PRODUCT_CATALOG_NAMESPACE = 'services'
