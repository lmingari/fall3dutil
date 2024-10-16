# Changelog
All notable changes to this project will be documented in this file.

## [2.1.0] - 2024-10-16

### Added
- Option to download CARRA dataset in model levels (65)
- CARRA can be optionally downloaded using a cropped domain

### Changed
- Now it is possible to choose between grib or netcdf format for ECMWF datasets
- Now it is possible to choose between east_domain and west_domain for CARRA datasets

### Removed
- Removed deprecated request parameters for ECMWF dataset request configuration

### Fixed
- Fixed compatibility with the New Climate Data Store (CDS)! (not stable yet)
