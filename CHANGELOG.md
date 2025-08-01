# Changelog

All notable changes to the SavePip project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-08-01
### Added
- Memory synchronization between requirements.txt and memory manager
- Improved tracking for packages in requirements.txt
- Debug logging for troubleshooting package installations
- Enhanced documentation in README.md

### Fixed
- Fixed issue with manually added packages missing from requirements.txt
- Corrected package synchronization logic between memory and requirements.txt
- Improved error handling in pip dependency saving

### Changed
- Updated code formatting for better readability
- Improved logging and error messages
- Refactored _save_pip_dependencies method for better reliability

## [0.1.1] - 2025-07-20
### Added
- Initial release with basic functionality
- Support for pip and conda package managers
- Category management for organizing dependencies
- Command-line interface

### Fixed
- Minor bug fixes and improvements

## [0.1.0] - 2025-07-15
### Added
- Initial prototype
- Basic package installation
- Requirements file generation
