# Changelog

(C) Copyright 2021-2025 Hewlett Packard Enterprise Development LP

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-11-26

### Changed
- Use the product-deletion-utility:1.0.2 image.

## [1.4.0] - 2025-02-13

### Changed
- Use the product-deletion-utility:1.0.1 image.

## [1.3.0] - 2023-08-10

### Changed
- Add logger module to write to a file and provide a new option --dry-run.

## [1.2.1] - 2023-07-12

### Changed
- Provide a new option --podman-options for users to provide arbitrary podman arguments to prodmgr.

## [1.2.0] - 2023-03-09

### Changed
- Launch the product-deletion-utility container for delete and uninstall actions.
- Launch the <product>-install-utility container for activate actions.
- Use the csm-docker-sle:15.4 image.

### Added
- Add the 'delete' action as an alias to 'uninstall'

## [1.1.6] - 2022-06-24

### Changed
- Changed the format of copyright text and added MIT License text in all of the
  source files.

## [1.1.5] - 2022-06-14

### Fixed
- Fixed builds of stable RPMs by running publishing step outside of container,
  and add Dockerfile which sets up build dependencies, so that the build does
  not need to run as root.

## [1.1.4] - 2022-06-08

### Fixed
- Fixed BuildRequires to require python3-setuptools.

## [1.1.3] - 2022-05-24

### Changed
- Made changes related to open sourcing of prodmgr.
    - Update Jenkinsfile to use csm-shared-library.
    - Add Makefile for building RPM package.

## [1.1.2] - 2022-01-04

### Added

- Added a man page for ``prodmgr``.

## [1.1.1] - 2021-11-29

### Changed

- Modified the RPM to not require ``kubectl`` so that it can be installed
  into the  NCN image.

## [1.1.0] - 2021-11-22

### Changed

- Removed the use of Python Kubernetes API.
- Removed Python packaging from the build and convert to RPM packaging.

## [1.0.1] - 2021-10-29

### Fixed

- Packaging fixes so that ``prodmgr`` can be installed via ``pip``.

## [1.0.0] - 2021-10-15

### Added

- Initial implementation of prodmgr command.
