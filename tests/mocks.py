"""
Fake data for unit tests for prodmgr.

(C) Copyright 2021 Hewlett Packard Enterprise Development LP.
"""

from yaml import safe_dump

SAT_VERSIONS = {
    '1.0.0': {
        'component_versions': {
            'docker': [
                {'name': 'cray/cray-sat', 'version': '1.0.0'},
                {'name': 'cray/sat-install-utility', 'version': '1.4.0'}
            ]
        }
    }
}

MOCK_PRODUCT_CATALOG_DATA = {
    'sat': safe_dump(SAT_VERSIONS)
}
