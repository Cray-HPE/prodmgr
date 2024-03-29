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
# Spec file for Product Manager CLI

%define man_subdir %{_mandir}/man8

Name: cray-prodmgr
Version: %(./tools/changelog.py ./CHANGELOG.md)
License: MIT
Release: %(echo ${BUILD_METADATA})
Source: %{name}-%{version}.tar.bz2
Summary: Shasta Product Manager CLI
Group: System/Management
BuildRoot: %{_topdir}
Vendor: Hewlett Packard Enterprise Company
# TODO(MTL-1570): It is currently impossible to install this package into the
# NCN image when kubectl is listed as a dependency, due to this package being
# installed before the kubectl is available.
#Requires: kubectl
Requires: podman
Requires: python3-PyYAML
BuildRequires: python3-setuptools
BuildRequires: python3-docutils

%description
The prodmgr command is responsible for launching product install utility and delete utility images.
It is used for activating (deprecated) and deleting versions of products.

%prep
%setup -n %{name}-%{version}

%build
# make man pages
cd man
make
cd -

%install
python3 setup.py install -O1 --root="$RPM_BUILD_ROOT" --record=INSTALLED_FILES \
                             --install-scripts=/usr/bin

# Install man pages
install -m 755 -d %{buildroot}/%{man_subdir}/
cp man/*.8 %{buildroot}/%{man_subdir}/

# This is a hack taken from the DST-EXAMPLES / example-rpm-python repo to get
# the package directory, i.e. /usr/lib/python3.6/site-packages/sat which is not
# included in the INSTALLED_FILES list generated by setup.py.
# TODO: Replace this hack with something better, perhaps using %python_sitelib
cat INSTALLED_FILES | grep __pycache__ | xargs dirname | xargs dirname | uniq >> INSTALLED_FILES

# Our top-level `prodmgr` script is currently installed by specifying our main
# function as an entry_point. Thus it is installed by `setup.py` above and
# listed in INSTALLED_FILES. If we change how that script is generated, we will
# need to manually install it here.

%files -f INSTALLED_FILES
%{man_subdir}/*.8.gz
