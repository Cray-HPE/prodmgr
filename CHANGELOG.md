# Changelog

(C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
