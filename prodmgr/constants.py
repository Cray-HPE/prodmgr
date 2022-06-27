#
# MIT License
#
# (C) Copyright 2021 Hewlett Packard Enterprise Development LP
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
Constant values for prodmgr.
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
