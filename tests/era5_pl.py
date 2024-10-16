#!/usr/bin/env python3
"""
Download ERA5 data (pressure levels) required by FALL3D model.
"""
import argparse
from fall3dutil import ERA5pl

def main():
    # Input parameters and options
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS,description=__doc__)
    parser.add_argument('-d', '--date',    help='Date range in format YYYYMMDD',   type=str,   nargs=2, metavar=('start_date','end_date'))
    parser.add_argument('-x', '--lon',     help='Longitude range',                 type=float, nargs=2, metavar=('lonmin', 'lonmax'))
    parser.add_argument('-y', '--lat',     help='Latitude range',                  type=float, nargs=2, metavar=('latmin', 'latmax'))
    parser.add_argument('-r', '--res',     help='Spatial resolution (deg)',        type=float,          metavar='resolution')
    parser.add_argument('-s', '--step',    help='Temporal resolution (h)',         type=int,            metavar='step')
    parser.add_argument('-f', '--format',  help='Format of output file',           type=str,            metavar='format', choices=['netcdf', 'grib']) 
    parser.add_argument('-b', '--block',   help='Block in the configuration file', type=str,            metavar='block')
    parser.add_argument('-i', '--input',   help='Configuration file',              type=str,            metavar='file')
    parser.add_argument('-v', '--verbose', help="Increase output verbosity",                            action="store_true")
    args = parser.parse_args()

    a = ERA5pl(args)
    a.retrieve()

if __name__ == '__main__':
    main()
