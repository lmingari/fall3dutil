import os
import getpass
import numpy as np
from datetime import datetime, timedelta
from netCDF4 import Dataset,date2num

class Dimension:
    def __init__(self,src,dimname):
        var = src.variables[dimname]
        self.dimname  = dimname
        self.data     = var[:]
        self.size     = var.size
        self.datatype = var.datatype
        self.atts     = var.__dict__

class OpenDAP:
    server  = ""
    dims    = {}
    vars3d  = {}
    vars4d  = {}
    def __init__(self, args):
        #time arguments
        self.date     = args.date
        self.cycle    = args.cycle
        self.step     = args.step
        self.it1      = args.time[0]
        self.it2      = args.time[1]+1
        self.time_ref = args.date + timedelta(hours=args.cycle)

        #lat arguments
        self.latmin = args.latmin
        self.latmax = args.latmax

        #lon arguments
        self.lonmin = args.lonmin
        self.lonmax = args.lonmax
        if args.lonmin<0: self.lonmin = args.lonmin + 360.0
        if args.lonmax<0: self.lonmax = args.lonmax + 360.0

        #spatial resolution
        self.res    = args.res

        #output file
        self.output = args.output

        #verbose option
        self.verbose = args.verbose

        #Source and Destination netCDF
        self.src    = None
        self.dst    = None

        #If use cyclic indexing for subsetting 
        #along longitude dimensions
        self.cyclic = False

        #Reference to variable dimensions
        self.dims_out = {}
        self.dims_in  = {}

    def open_remote(self):
        #get url for the first time.
        url = self._getURL(self.time_ref)

        if self.verbose: print("opening:", url)

        #dimensions are read only for 
        #the first time
        self.src     = Dataset(url)
        self.time_in = Dimension(self.src,self.dims["time"])
        self.levs_in = Dimension(self.src,self.dims["lev"])
        self.lats_in = Dimension(self.src,self.dims["lat"])
        self.lons_in = Dimension(self.src,self.dims["lon"])

    def open_local(self):
        if self.verbose: print("creating output file:", self.output) 
        self.dst = Dataset(self.output,"w")

        #level indexes
        self.iz1=0
        self.iz2=self.levs_in.size

        #latitude indexes
        iy1 = np.argmin(np.ma.abs(self.lats_in.data-self.latmin))
        iy2 = np.argmin(np.ma.abs(self.lats_in.data-self.latmax))
        if iy1>iy2:
            iy1,iy2 = iy2,iy1
        iy2 += 1
        self.iy1 = iy1
        self.iy2 = iy2

        #longitude indexes
        ix1 = np.argmin(np.ma.abs(self.lons_in.data-self.lonmin))
        ix2 = np.argmin(np.ma.abs(self.lons_in.data-self.lonmax))
        if ix1>ix2:
            #Cyclic indexing
            self.cyclic     = True
            ix2            += 1
            ix1             = self.lons_in.size - ix1
        elif ix1==ix2:
            #Global data
            ix1         = 0
            ix2         = self.lons_in.size
        else:
            ix2        += 1
        self.ix1 = ix1
        self.ix2 = ix2

        #dimension output sizes
        self.nt_out = self.it2-self.it1
        self.nz_out = self.iz2-self.iz1
        self.ny_out = self.iy2-self.iy1
        if self.cyclic:
            self.nx_out = self.ix1+self.ix2
        else:
            self.nx_out = self.ix2-self.ix1

        #create output dimensions 
        self.dst.createDimension("time", None       )
        self.dst.createDimension("lev",  self.nz_out)
        self.dst.createDimension("lat",  self.ny_out)
        self.dst.createDimension("lon",  self.nx_out)

        #create coordinates variables
        var_out = self.dst.createVariable("time", self.levs_in.datatype, "time")
        var_out.setncatts(self.time_in.atts)

        var_out = self.dst.createVariable("lev", self.levs_in.datatype, "lev")
        var_out.setncatts(self.levs_in.atts)

        var_out = self.dst.createVariable("lat", self.lats_in.datatype, "lat")
        var_out.setncatts(self.lats_in.atts)

        var_out = self.dst.createVariable("lon", self.lons_in.datatype, "lon")
        var_out.setncatts(self.lons_in.atts)

        #create 3D variables
        dimensions = ('time', 'lat', 'lon')
        for varname_out, varname_in in self.vars3d.items():
            var_in  = self.src.variables[varname_in]
            var_out = self.dst.createVariable(varname_out,var_in.datatype,dimensions)
            var_out.setncatts(var_in.__dict__)
            #
            self.dims_in[varname_in]   = var_in.shape    
            self.dims_out[varname_out] = var_out.shape

        #create 4D variables
        dimensions = ('time', 'lev', 'lat', 'lon')
        for varname_out, varname_in in self.vars4d.items():
            var_in  = self.src.variables[varname_in]
            var_out = self.dst.createVariable(varname_out,var_in.datatype,dimensions)
            var_out.setncatts(var_in.__dict__)
            #
            self.dims_in[varname_in]   = var_in.shape
            self.dims_out[varname_out] = var_out.shape

    def save_data(self):
        if self.verbose: print("saving data")
        #write coordinates variables
        if self.verbose: print("saving coordinate variables...")
        self._write_time()
        self.dst.variables["lev"][:]  = self.levs_in.data[self.iz1:self.iz2]
        self.dst.variables["lat"][:]  = self.lats_in.data[self.iy1:self.iy2]
        if self.cyclic:
            lons_out             = np.empty(self.nx_out)
            lons_out[:self.ix1]  = self.lons_in.data[-self.ix1:]
            lons_out[-self.ix2:] = self.lons_in.data[:self.ix2]
            lons_out[lons_out>=180.0] = lons_out[lons_out>=180.0] - 360.0 
            self.dst.variables["lon"][:] = lons_out[:]
        else:
            self.dst.variables["lon"][:] = self.lons_in.data[self.ix1:self.ix2]

        self._write_vars()

        if self.src.isopen():
            print("closing remote connection")
            self.src.close()
        if self.dst.isopen:
            print("closing output file")
            self.dst.close()

    def _getURL(self,time_url):
        return ""

    def _write_time(self):
        self.dst.variables["time"][:] = self.time_in.data[self.it1:self.it2] 

    def _write_vars(self):
        pass

class Gdas(OpenDAP):
    server  = "rda.ucar.edu" 
    dims    = {'time'  : 'time', 
               'lev'   : 'isobaric3', 
               'lat'   : 'lat',
               'lon'   : 'lon' 
               }
    vars3d  = {'lnd'   : 'Land_cover_0__sea_1__land_surface',
               'hgt'   : 'Geopotential_height_surface',
               'psfc'  : 'Pressure_surface',
               'u10'   : 'u-component_of_wind_height_above_ground',
               'v10'   : 'v-component_of_wind_height_above_ground',
               'smois' : 'Volumetric_Soil_Moisture_Content_depth_below_surface_layer',
               'pblh'  : 'Planetary_Boundary_Layer_Height_surface',
               't2'    : 'Temperature_height_above_ground',
               }
    vars4d  = {'t'     : 'Temperature_isobaric',
               'u'     : 'u-component_of_wind_isobaric',
               'v'     : 'v-component_of_wind_isobaric',
               'w'     : 'Vertical_velocity_pressure_isobaric',
               'z'     : 'Geopotential_height_isobaric',
               'rh'    : 'Relative_humidity_isobaric',
               }

    def __init__(self, args):
        super().__init__(args)
        dt = timedelta(hours=self.step)
        self.times    = [self.time_ref+it*dt for it in range(self.it1,self.it2)]
        #Update reference time
        self.time_ref = self.times[0]

        #reading username and password
        self.pwfile  = '.rdamspw'
        self.username, self.password = self.__getUserPass()

    def _getURL(self,time_url):
        URL      = "https://{user}:{psw}@{server}/{thredds}/{datatype}/{yy}/{yy}{mm}/{fname}"
        hfcst    = time_url.hour%6                   #Forecast hour
        time_anl = time_url - timedelta(hours=hfcst) #Analysis datetime
        if self.res==0.25:
            fname = "gdas1.fnl0p25.{yyyymmddhh}.f{hfcst:02d}.grib2".format(yyyymmddhh = time_anl.strftime("%Y%m%d%H"),hfcst = hfcst)
        else:
            fname = ""
        return URL.format(user     = self.username.replace('@','%40'), 
                          psw      = self.password,
                          server   = self.server,
                          datatype = "ds083.3",
                          thredds  = "thredds/dodsC/files/g",
                          fname    = fname,
                          yy       = time_anl.strftime("%Y"),
                          mm       = time_anl.strftime("%m") )

    def __getUserPass(self):
        #Check and read/write username and password
        if os.path.isfile(self.pwfile) and os.path.getsize(self.pwfile) > 0:
            with open(self.pwfile,"r") as f:
                pwstring = f.read()
                username,password = pwstring.split(',',2)
        else:
            username = input("Enter your RDA username or email: ")
            password = getpass.getpass("Enter your RDA password: ")
            print("Saving confidential information in", self.pwfile)
            with open(self.pwfile, "w") as f:
                pwstring = "{usr},{psw}".format(usr=username,psw=password)
                f.write(pwstring)
        return (username,password)

    def _write_time(self):
        self.dst.variables["time"][:] = date2num(self.times,
                                                 units    = self.time_in.atts["units"], 
                                                 calendar = self.time_in.atts["calendar"] )

    def _write_vars(self):
        for it, time in enumerate(self.times):
            if self.verbose: print("Working for time", time)
            if it>0:
                url = self._getURL(time)
                if self.verbose: print("opening", url)
                src = Dataset(url)
            else:
                src = self.src
            #
            #Write 3D variables
            for varname_out, varname_in in self.vars3d.items():
                range_in = len(self.dims_in[varname_in])
                if range_in==3:
                    if self.cyclic:
                        self.dst.variables[varname_out][it,:,:self.ix1]  = src.variables[varname_in][0,self.iy1:self.iy2,-self.ix1:]
                        self.dst.variables[varname_out][it,:,-self.ix2:] = src.variables[varname_in][0,self.iy1:self.iy2,:self.ix2]
                    else:
                        self.dst.variables[varname_out][it,:,:] = src.variables[varname_in][0,self.iy1:self.iy2,self.ix1:self.ix2]
                elif range_in==4:
                    if self.cyclic:
                        self.dst.variables[varname_out][it,:,:self.ix1]  = src.variables[varname_in][0,0,self.iy1:self.iy2,-self.ix1:]
                        self.dst.variables[varname_out][it,:,-self.ix2:] = src.variables[varname_in][0,0,self.iy1:self.iy2,:self.ix2]
                    else:
                        self.dst.variables[varname_out][it,:,:] = src.variables[varname_in][0,0,self.iy1:self.iy2,self.ix1:self.ix2]
                else:
                    print("input variable {var_name} with range {var_range} rejected".format(var_name=varname_in, var_range=range_in) )
            #
            #Write 4D variables
            for varname_out, varname_in in self.vars4d.items():
                nz_in = self.dims_in[varname_in][1]
                nz_out = self.nz_out
                if nz_in==nz_out:
                    iz1=self.iz1
                    iz2=self.iz2
                elif nz_in<nz_out:
                    iz1=nz_out-nz_in
                    iz2=nz_out
                else:
                    print("rejecting variable {varname}".format(varname_in))
                    continue
                if self.cyclic:
                    self.dst.variables[varname_out][it,iz1:iz2,:,:self.ix1]  = src.variables[varname_in][0,:,self.iy1:self.iy2,-self.ix1:]
                    self.dst.variables[varname_out][it,iz1:iz2,:,-self.ix2:] = src.variables[varname_in][0,:,self.iy1:self.iy2,:self.ix2]
                else:
                    self.dst.variables[varname_out][it,iz1:iz2,:,:] = src.variables[varname_in][0,:,self.iy1:self.iy2,self.ix1:self.ix2]
            src = None

class GFS(OpenDAP):
    server  = "nomads.ncep.noaa.gov:9090"
    dims    = {'time'  : 'time', 
               'lev'   : 'lev', 
               'lat'   : 'lat',
               'lon'   : 'lon' 
               }
    vars3d  = {'lnd'   : 'landsfc',
               'hgt'   : 'hgtsfc',
               'psfc'  : 'pressfc',
               'u10'   : 'ugrd10m',
               'v10'   : 'vgrd10m',
               'smois' : 'soilw0_10cm',
               'pblh'  : 'hpblsfc',
               't2'    : 'tmp2m',
               'prate' : 'pratesfc',
               }
    vars4d  = {'t'     : 'tmpprs',
               'u'     : 'ugrdprs',
               'v'     : 'vgrdprs',
               'w'     : 'vvelprs',
               'z'     : 'hgtprs',
               'rh'    : 'rhprs',
               }

    def __init__(self, args):
        super().__init__(args)

    def _getURL(self,time_url):
        URL = "https://{server}/{thredds}/{datatype}/gfs{date}/{fname}"
        if self.res==0.25 and self.step==1:
            datatype = "gfs_0p25_1hr"
        elif self.res==0.25 and self.step==3:
            datatype = "gfs_0p25"
        elif self.res==0.5 and self.step==3:
            datatype = "gfs_0p50"
        elif self.res==1 and self.step==12:
            datatype = "gfs_1p00"
        else:
            datatype = ""
        fname = "{datatype}_{HH}z".format(datatype=datatype, HH=time_url.strftime("%H"))
        return URL.format(server   = self.server,
                          datatype = datatype,
                          thredds  = "dods",
                          fname    = fname,
                          date     = time_url.strftime("%Y%m%d") )

    def _write_vars(self):
        #
        for varname_out, varname_in in self.vars3d.items():
            if self.verbose: print("saving variable:", varname_in) 
            range_in = len(self.dims_in[varname_in])
            if range_in==3:
                if self.cyclic:
                    self.dst.variables[varname_out][:,:,:self.ix1]  = self.src.variables[varname_in][self.it1:self.it2,self.iy1:self.iy2,-self.ix1:]
                    self.dst.variables[varname_out][:,:,-self.ix2:] = self.src.variables[varname_in][self.it1:self.it2,self.iy1:self.iy2,:self.ix2]
                else:
                    self.dst.variables[varname_out][:,:,:] = self.src.variables[varname_in][self.it1:self.it2,self.iy1:self.iy2,self.ix1:self.ix2]
            elif range_in==4:
                if self.cyclic:
                    self.dst.variables[varname_out][:,:,:self.ix1]  = self.src.variables[varname_in][self.it1:self.it2,0,self.iy1:self.iy2,-self.ix1:]
                    self.dst.variables[varname_out][:,:,-self.ix2:] = self.src.variables[varname_in][self.it1:self.it2,0,self.iy1:self.iy2,:self.ix2]
                else:
                    self.dst.variables[varname_out][:,:,:] = self.src.variables[varname_in][self.it1:self.it2,0,self.iy1:self.iy2,self.ix1:self.ix2]
            else:
                print("input variable {var_name} with range {var_range} rejected".format(var_name=varname_in, var_range=range_in) )
        #
        it_dst = 0
        for it_src in range(self.it1,self.it2):
            print("Working for time", it_dst, it_src)
            for varname_out, varname_in in self.vars4d.items():
                if self.verbose: print("saving variable:", varname_in) 
                range_in = len(self.dims_in[varname_in])
                if range_in==4:
                    if self.cyclic:
                        self.dst.variables[varname_out][it_dst,:,:,:self.ix1]  = self.src.variables[varname_in][it_src,:,self.iy1:self.iy2,-self.ix1:]
                        self.dst.variables[varname_out][it_dst,:,:,-self.ix2:] = self.src.variables[varname_in][it_src,:,self.iy1:self.iy2,:self.ix2]
                    else:
                        self.dst.variables[varname_out][it_dst,:,:,:] = self.src.variables[varname_in][it_src,:,self.iy1:self.iy2,self.ix1:self.ix2]
                else:
                    print("input variable {var_name} with range {var_range} rejected".format(var_name=varname_in, var_range=range_in) )
            #
            it_dst += 1



