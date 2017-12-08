# Change Log
All notable changes to this project will be documented in this file. See [Keep a
CHANGELOG](http://keepachangelog.com/) for how to update this file. This project
adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased][unreleased]

## [0.1.1] - 2017-12-08
### Changed
- Changed how thread local variables are handled in order to fix issues with threads losing honeybadger config data

## [0.1.0] - 2017-11-03
### Added
- Block calls to honeybadger server when development like environment unless 
  explicitly forced.

### Changed
- Remove unused `trace_threshold` config option.

## [0.0.6] - 2017-03-27
### Fixed
- Added support for Django 1.10 middleware changes.

## [0.0.5] - 2016-10-11
### Fixed
- Python 3 setup.py bug.

## [0.0.4] - 2016-10-11
### Fixed
- setup.py version importing bug.

## [0.0.3] - 2016-10-11
### Fixed
- Python 3 bug in `utils.filter_dict` - vineesha

## [0.0.2][0.0.2]
### Fixed
- Add Python 3 compatibility. -@demsullivan
- Convert exception to error message using `str()` (#13) -@krzysztofwos
