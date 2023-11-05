#!/usr/bin/env python3
"""
Download CARRA data (pressure levels) required by FALL3D model.
"""
import argparse
from fall3dutil import CARRApl

def main():
    # Input parameters and options
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS,description=__doc__)
    parser.add_argument('-d', '--date',    help='Date range in format YYYYMMDD',   type=str,   nargs=2, metavar=('start_date','end_date'))
    parser.add_argument('-s', '--step',    help='Temporal resolution (h)',         type=int,            metavar='step')
    parser.add_argument('-b', '--block',   help='Block in the configuration file', type=str,            metavar='block')
    parser.add_argument('-i', '--input',   help='Configuration file',              type=str,            metavar='file')
    parser.add_argument('-v', '--verbose', help="increase output verbosity",                            action="store_true")
    args = parser.parse_args()

    a = CARRApl(args)
    a.retrieve()

if __name__ == '__main__':
    main()
