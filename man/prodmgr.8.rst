=========
 PRODMGR
=========

-------------------
Product Manager CLI
-------------------

:Author: Hewlett Packard Enterprise Development LP.
:Copyright: Copyright 2021 Hewlett Packard Enterprise Development LP.
:Manual section: 8

SYNOPSIS
========

**prodmgr** ACTION PRODUCT VERSION [options]

DESCRIPTION
===========

prodmgr is the CLI for Shasta uninstall and downgrade. It works by running
product-specific install utility container images that provide the functionality
that can "uninstall" or "activate" a given version of a given product.

ARGUMENTS
=========

*ACTION*
    The action to perform on the specified product. "uninstall" or "activate".

*PRODUCT*
    The name of the product for which to perform the specified action.

*VERSION*
    The version of the product for which to perform the specified action.

OPTIONS
=======

**-h, --help**

**--cert-src-dir**
    The directory on the host containing trusted certificates.
    Default: "/etc/pki/trust/anchors"

**--cert-target-dir**
    The directory where trusted certificates should be mounted in the
    container. Default: "/usr/local/share/ca-certificates"

**--kube-config-src-file**
    The location of the kubernetes configuration file on the host.
    Default: "/etc/kubernetes/admin.conf"

**--kube-config-target-file**
    The location where the kubernetes configuration file should be mounted in
    the container. Default: "$HOME/.kube/config"

**--product-catalog-name**
    The name of the product catalog Kubernetes ConfigMap.
    Default: "cray-product-catalog"

**--product-catalog-namespace**
    The namespace of the product catalog Kubernetes ConfigMap.
    Default: "services"

**--container-registry-hostname**
    The hostname of the container image registry.
    Default: "registry.local"

EXAMPLES
========

Uninstall SAT version 2.2.10.

::

    # prodmgr uninstall sat 2.2.10
    Running cray/sat-install-utility:1.4.0-20211122193744_8cc33b0
    cray/cray-sat:3.12.0-20211207204308_4c03082 has been removed.
    cray/sat-cfs-install:1.0.3-20210907184559_253262a has been removed.
    cray/sat-install-utility:1.4.0-20211122193744_8cc33b0 has been removed.
    Repository sat-2.2.10 has been removed.
    Deleted sat-2.2.10 from product catalog.


Activate SAT version 2.2.10.

::

    # prodmgr activate sat 2.2.10
    Running cray/sat-install-utility:1.4.0-20211122193744_8cc33b0
    Updated group repository sat-sle-15sp2 with member repositories: [sat-2.2.10-sle-15sp2]
    Set sat-2.2.10 as active in the product catalog.
    Updated CFS configurations: [ncn-personalization]

