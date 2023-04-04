#!/usr/bin/env python3
import argparse
from fall3dutil import GFS

def main():
    # Input parameters and options
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS,description=__doc__)
    parser.add_argument('-x', '--lon',     help='Longitude range',                 type=float, nargs=2, metavar=('lonmin', 'lonmax'))
    parser.add_argument('-y', '--lat',     help='Latitude range',                  type=float, nargs=2, metavar=('latmin', 'latmax'))
    parser.add_argument('-t', '--time',    help='Forecast time range (h)',         type=int,   nargs=2, metavar=('tmin',   'tmax'))
    parser.add_argument('-r', '--res',     help='Spatial resolution (deg)',        type=float,          metavar='resolution', choices=(0.25, 0.5, 1.0) )
    parser.add_argument('-c', '--cycle',   help='Cycle',                           type=int,            metavar='cycle',      choices=(0,6,12,18))
    parser.add_argument('-s', '--step',    help='Temporal resolution (h)',         type=int,            metavar='step',       choices=(1, 3, 12))
    parser.add_argument('-b', '--block',   help='Block in the configuration file', type=str,            metavar='block')
    parser.add_argument('-i', '--input',   help='Configuration file',              type=str,            metavar='file')
    parser.add_argument('-v', '--verbose', help="increase output verbosity",                            action="store_true")
    parser.add_argument('-d', '--date',    help='Initial date in format YYYYMMDD', type=str,            metavar='start_date')
    args = parser.parse_args()

    a = GFS(args)
    a.save_data()

if __name__ == '__main__':
    main()
