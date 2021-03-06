# prodmgr

`prodmgr` is the CLI for Shasta uninstall and downgrade. It works by running
product-specific install utility container images.

## Assumptions made by prodmgr

For a product to work with `prodmgr`, an install utility image must exist
for that product, specifically for the version of the product being operated
on.

This section documents the assumptions that `prodmgr` makes about that image.

### Install Utility Image

The install utility image:

* Is specific to the individual product and provides logic for uninstall
  and activation.
* Must be named `cray/PRODUCT-install-utility`.
* Must be installed (uploaded to Nexus) with the associated product stream,
  and information about it must be added to the product catalog at install
  time.
* Must have a main entry point script that accepts specific CLI arguments (see
  [below](#command-line-arguments)).

When running `prodmgr ACTION PRODUCT`, `prodmgr` will assume there is an
image named `cray/PRODUCT-install-utility` in the container image registry. The
version is looked up in the `cray-product-catalog` ConfigMap. For example, if
the following is contained in the product catalog:


```
sat:
  2.2.10:
    docker:
      - name: cray/sat-install-utility
        version: 3.4.5
```

Then running `prodmgr uninstall sat 2.2.10` would result in running
version 3.4.5 of `cray/sat-install-utility`.

### Command-line Arguments

The install utility image default entry point script:

* Must accept an 'action' (`uninstall` or `activate`) as its first positional
  argument.
* Must accept a 'version' as its second positional argument.
* Must accept `--product-catalog-name` and `--product-catalog-namespace`
  arguments.

For example, the default entry point of `cray/sat-install-utility` accepts the
following command-line arguments:

```
positional arguments:
  {uninstall,activate}  Specify the operation to execute on a product.
  version               Specify the version of the product to operate on.

optional arguments:
  -h, --help            show this help message and exit
  --nexus-url NEXUS_URL
                        Override the base URL of Nexus.
                        Default: "https://packages.local"
  --docker-url DOCKER_URL
                        Override the base URL of the Docker registry.
                        Default: "https://registry.local"
  --product-catalog-name PRODUCT_CATALOG_NAME
                        The name of the product catalog Kubernetes ConfigMap
  --product-catalog-namespace PRODUCT_CATALOG_NAMESPACE
                        The namespace of the product catalog Kubernetes ConfigMap
```

The specific requirements of the entry point command-line arguments are based
on how `prodmgr` parses command-line options and how it invokes the install
utility container. Here are the positional arguments that `prodmgr` parses:

```
positional arguments:
  {uninstall,activate}  Specify the operation to execute on a product.
  product               The name of the product to uninstall or activate.
  version               Specify the version of the product to operate on.
```

Two positional arguments, `action` (`uninstall`, `activate`) and `version` will
be passed to the underlying container, therefore the underlying container must
accept these as positional arguments. However, the name of the product is not
needed because the underlying container is already specific to that product.

Here are the optional arguments that `prodmgr` parses:

```
optional arguments:
  -h, --help            show this help message and exit
  --product-catalog-name PRODUCT_CATALOG_NAME
                        The name of the product catalog Kubernetes ConfigMap
                        Default: "cray-product-catalog"
  --product-catalog-namespace PRODUCT_CATALOG_NAMESPACE
                        The namespace of the product catalog Kubernetes
                        ConfigMap
                        Default: "services"
  --kube-config-src-file KUBE_CONFIG_SRC_FILE
                        The location of the kubernetes configuration file on
                        the host
                        Default: "/etc/kubernetes/admin.conf"
  --kube-config-target-file KUBE_CONFIG_TARGET_FILE
                        The location where the kubernetes configuration file
                        should be mounted in the container
                        Default: "$HOME/.kube/config"
  --cert-src-dir CERT_SRC_DIR
                        The directory on the host containing trusted
                        certificates
                        Default: "/etc/pki/trust/anchors"
  --cert-target-dir CERT_TARGET_DIR
                        The directory where trusted certificates should be
                        mounted in the container
                        Default: "/usr/local/share/ca-certificates"
  --container-registry-hostname CONTAINER_REGISTRY_HOSTNAME
                        The hostname of the container image registry
                        Default: "registry.local"
```

The arguments `--product-catalog-name` and `--product-catalog-namespace` will
be passed to the underlying container, therefore the underlying container
must also accept these arguments, with the same names.
