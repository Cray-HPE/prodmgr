# prodmgr

`prodmgr` is the CLI for Shasta activation or deletion of versions of products. It works by running a generic deletion container to delete product components. When asked to activate a component, prodmgr will fall back to using a product-specific install utility container. This fall-back approach is to support backwards compatibility during a period of deprecation of the 'activate' command.

## Assumptions made by prodmgr

A generic image already exists for deleting products with `prodmgr`. Products, therefore, do not need to do anything or provide any image to be able to delete their components.

However, for a product to be activated with `prodmgr`, an install utility image must exist for that product, specifically for the version of the product being operated on. The ability to activate a product is supported for backwards compability and has been deprecated going forward, meaning at some point it will be removed.

This section documents the assumptions that `prodmgr` makes about that image.

### Install Utility Image

NOTE: activating a product has been deprecated, and products should not rely
on this. This is only being supported for legacy products that already provided
an image explicitly for this purpose. Products do not need to create this image
if all they want to do is delete their components. A generic image is provided
for that.

The install utility image:

* Is specific to the individual product and provides logic for activation.
* Must be named `cray/PRODUCT-install-utility`.
* Must be installed (uploaded to Nexus) with the associated product stream,
  and information about it must be added to the product catalog at install
  time.
* Must have a main entry point script that accepts specific CLI arguments (see
  [below](#command-line-arguments)).

When running `prodmgr activate PRODUCT`, `prodmgr` will assume there is an
image named `cray/PRODUCT-install-utility` in the image registry. The
version is looked up in the `cray-product-catalog` ConfigMap. For example, if
the following is contained in the product catalog:


```yaml
sat:
  2.2.10:
    docker:
      - name: cray/sat-install-utility
        version: 3.4.5
```

Then running `prodmgr activate sat 2.2.10` would result in running
version 3.4.5 of `cray/sat-install-utility`.

### Command-line Arguments

The install utility image default entry point script:

* Must accept an 'action' as its first positional. It is only required to support the `activate` action.
  argument.
* Must accept a 'version' as its second positional argument.
* Must accept `--product-catalog-name` and `--product-catalog-namespace`
  arguments.

For example, the default entry point of `cray/sat-install-utility` accepts the
following command-line arguments:

```text
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

```text
positional arguments:
  {delete,uninstall,activate}
                        Specify the operation to execute on a product. Note:
                        activate is deprecated. uninstall is deprecated in
                        favor of delete.
  product               The name of the product to delete or activate.
  version               Specify the version of the product to operate on.

```

Two positional arguments, `action` (`uninstall`, `activate`) and `version` will
be passed to the underlying container, therefore the underlying container must
accept these as positional arguments. However, the name of the product is not
needed because the underlying container is already specific to that product.

Here are the optional arguments that `prodmgr` parses:

```text
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
  --deletion-image-name DELETION_IMAGE_NAME
                        The full path and file name of the deletion image
  --deletion-image-version DELETION_IMAGE_VERSION
                        The version of the deletion image
  --csm-version CSM_VERSION
                        The version of CSM from whence to query the deletion
                        image
  --extra-podman-config EXTRA_PODMAN_CONFIG
                        Additional podman options when launching the
                        deletion/install utility using podman container
                        engine(Eg: --extra-podman-config "--mount
                        type=bind,src=<src>,target=<target> --no-hosts --name
                        deletion-container")
  -d, --dry-run         Lists the components that would be deleted for the
                        provided product:version
```

The arguments `--product-catalog-name` and `--product-catalog-namespace` will
be passed to the underlying container. Therefore, the underlying container
must also accept these arguments with the same names.

# Generic Product Deletion Container

The product-deletion-utlity container serves as a generic  deletion container.
This container uses the cray-product-catalog to identify the components that
have been installed by the product version.

The below example is for the `cos` product version `2.5.101`:

```yaml

  cos: |
    2.5.101:
      component_versions:
        docker:
        - name: cray/cray-cos-config-service
          version: 1.0.3
        - name: cray/cray-cps-cm
          version: 2.8.6
        helm:
        - name: cos-sle15sp4-artifacts
          version: 2.1.18
        - name: cos-config-service
          version: 1.0.3
        manifests:
        - config-data/argo/loftsman/cos/2.5.101/manifests/cos-services.yaml
        repositories:
        - name: cos-2.5.101-sle-15sp4
          type: hosted
        - members:
          - cos-2.5.101-sle-15sp4
          name: cos-2.5-sle-15sp4
          type: group
        - name: cos-2.5.101-net-sle-15sp4-shs-2.0
          type: hosted
      configuration:
        clone_url: https://vcs.cmn.mug.hpc.amslabs.hpecorp.net/vcs/cray/cos-config-management.git
        commit: fe2edd67af6613550a20118a6f4d8295aeb9d59f
        import_branch: cray/cos/2.5.101
        import_date: 2023-08-07 10:47:48.472277
        ssh_url: git@vcs.cmn.mug.hpc.amslabs.hpecorp.net:cray/cos-config-management.git
      images: {}
      recipes:
        cray-shasta-compute-sles15sp4.noarch-2.5.30:
          id: a519dc00-8c2e-48cd-8344-7bfe4d05ff3

```
As mentioned in the above section (Command-line Arguments) the generic deletion container is used when the `prodmgr` parses the positional argument `delete`. All the optional arguments for the `prodmgr` are valid for this container.

This container fetches the components of a product version from the cray-product-catalog and queries different repositories like docker, nexus, s3, et.al and deletes the artifacts across these repositories if there are no dependencies with other versions of the same product or different products.

Finally, it also removes the entry from the cray-product-catalog.

`Note:`The --dry-run option can be used to run the generic deletion container to know the effect of deletion without actual deletion of components for a product version.

# Unit tests
Run the unit tests using the following command from the base directory.
PYTHONPATH=$(pwd) python3 tests/test_main.py
