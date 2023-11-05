from .configuration import Config
import cdsapi
import warnings

class ECMWF(Config):
    '''
    Base object to request and download  
    Weather Files from ECMWF using the Climate 
    Data Store (CDS) Application Program Interface (API)

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined
    '''
    def __init__(self, args):
        super().__init__(args)
        if self.verbose: self.printInfo()

    def retrieve(self):
        '''Request and download data using the CDS API'''
        params   = self._getParams()
        database = self._getDatabase()
        fname    = self._getFname()
        if self.verbose: print(f"Requesting file {fname}")
        try:
            c = cdsapi.Client()
        except Exception as e:
            msg = f"{e}\n" 
            msg += "In order to install the CDS API key follow the instruction here: https://cds.climate.copernicus.eu/api-how-to"
            raise Exception(msg)
        c.retrieve(database,params,fname)

    def _getParams(self):
        '''Define the config dictionary required by CDS'''
        return {}

    def _getDatabase(self):
        '''Define the database required by CDS'''
        return ""

    def _getFname(self):
        '''Define the output filename'''
        return "output.nc"

    @Config.date.setter
    def date(self,value):
        super(ECMWF,type(self)).date.fset(self,value)
        nvalue = len(self._date)
        if nvalue > 1:
            start_date, end_date = self._date[:2]
            if start_date>end_date:
                warnings.warn("date_start > date_end. Swaping dates")
                self._date = [end_date,start_date]
            else:
                self._date = [start_date,end_date]
        elif nvalue == 1:
            self._date *= 2
            warnings.warn("Using same date for date_start and date_end")
        else:
            raise ValueError("Missing mandatory argument: date")

class ERA5(ECMWF):
    '''
    Base object to request and download ERA5 
    Weather Files from ECMWF using the Climate 
    Data Store (CDS) Application Program Interface (API)

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined
    '''

    attrs = {
         'lon':        'float2',
         'lat':        'float2',
         'res':        'float',
         'step':       'int',
         'verbose':    'bool',
         'date':       'str',
        }

    def __init__(self, args):
        super().__init__(args)

    def _getParams(self):
        '''Define the config dictionary required by CDS'''
        params = {'format': 'netcdf'}
        params['grid'] = "{res}/{res}".format(res=self.res)
        #North/West/South/East
        params['area'] = "{latmax}/{lonmin}/{latmin}/{lonmax}".format(
                lonmin=self.lon[0],
                lonmax=self.lon[1],
                latmin=self.lat[0],
                latmax=self.lat[1])
        return params

    def _backExt(self):
        """Check if extended dataset is required"""
        output = False
        if self.date[0].year<1950:
            raise ValueError("Not available data for the requested date")
        elif self.date[0].year<1979:
            warnings.warn("Requesting ERA5 back extension 1950-1978 (Preliminary version)")
            output = True
        return output

    @Config.lon.setter
    def lon(self,value):
        """western longitudes must be given as negative numbers"""
        super(ERA5,type(self)).lon.fset(self,value)
        self._lon = [((lon-180.)%360)-180. for lon in self._lon]

class ERA5ml(ERA5):
    '''
    ERAml object to request and download ERA5 
    reanalysis (model levels) files from ECMWF 
    using the Climate Data Store (CDS) Application 
    Program Interface (API).

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined

    Attributes
    ----------
    lon : [float]
        Longitudes range

    lat : [float]
        Latitudes range

    res : float
        Resolution in deg
    
    step : int
        Time step in hours
    
    verbose : bool
        If print addition information
    
    date : [datetime]
        Start and End dates in a 2-element list
    '''
    def __init__(self, args):
        super().__init__(args)

    def _getParams(self):
        '''Define the config dictionary required by CDS'''
        params = super()._getParams()

        date1 = self.date[0].strftime("%Y-%m-%d")
        date2 = self.date[1].strftime("%Y-%m-%d")
        time  = [f"{h:02d}" for h in range(0,24,self.step)]

        #Parameters
        params['class']    = 'ea'
        params['expver']   = '1'
        params['stream']   = 'oper'
        params['type']     = 'an'
        params['time']     = "/".join(time)
        params['date']     = f"{date1}/to/{date2}"
        params['levtype']  = 'ml'
        params['param']    = '129/130/131/132/133/135/152'
        params['levelist'] = '1/to/137'

        return params

    def _getDatabase(self):
        '''Define the database required by CDS'''
        if self._backExt():
            database = 'reanalysis-era5-complete-preliminary-back-extension'
        else:
            database = 'reanalysis-era5-complete'
        return database

    def _getFname(self):
        '''Define the output filename'''
        date1 = self.date[0].strftime("%Y%m%d")
        date2 = self.date[1].strftime("%Y%m%d")
        fname = f"era5.ml.{date1}-{date2}.nc" 
        return fname

class ERA5pl(ERA5):
    '''
    ERA5pl object to request and download ERA5 
    reanalysis (pressure levels) files from ECMWF 
    using the Climate Data Store (CDS) Application 
    Program Interface (API).

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined

    Attributes
    ----------
    lon : [float]
        Longitudes range

    lat : [float]
        Latitudes range

    res : float
        Resolution in deg
    
    step : int
        Time step in hours
    
    verbose : bool
        If print addition information
    
    date : [datetime]
        Start and End dates in a 2-element list
    '''

    var_list = [
        'geopotential',
        'specific_humidity',
        'temperature',
        'u_component_of_wind',
        'v_component_of_wind',
        'vertical_velocity',
        ]

    lev_list = [
        '1','2','3','5','7',
        '10','20','30','50','70',
        '100','125','150','175',
        '200','225','250',
        '300','350',
        '400','450',
        '500','550',
        '600','650',
        '700','750','775',
        '800','825','850','875',
        '900','925','950','975',
        '1000'
        ]

    def __init__(self, args):
        super().__init__(args)

    def _getParams(self):
        '''Define the config dictionary required by CDS'''
        params = super()._getParams()

        date1 = self.date[0].strftime("%Y-%m-%d")
        date2 = self.date[1].strftime("%Y-%m-%d")
        time  = [f"{h:02d}:00" for h in range(0,24,self.step)]

        #Parameters
        params['product_type']   = 'reanalysis'
        params['time']           = time
        params['date']           = f"{date1}/{date2}"
        params['variable']       = self.var_list
        params['pressure_level'] = self.lev_list

        return params

    def _getDatabase(self):
        '''Define the database required by CDS'''
        if self._backExt():
            database = 'reanalysis-era5-pressure-levels-preliminary-back-extension'
        else:
            database = 'reanalysis-era5-pressure-levels'
        return database

    def _getFname(self):
        '''Define the output filename'''
        date1 = self.date[0].strftime("%Y%m%d")
        date2 = self.date[1].strftime("%Y%m%d")
        fname = f"era5.pl.{date1}-{date2}.nc" 
        return fname

class ERA5sfc(ERA5):
    '''
    ERAsfc object to request and download ERA5 
    reanalysis (single level) files from ECMWF 
    using the Climate Data Store (CDS) Application 
    Program Interface (API).

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined

    Attributes
    ----------
    lon : [float]
        Longitudes range

    lat : [float]
        Latitudes range

    res : float
        Resolution in deg
    
    step : int
        Time step in hours
    
    verbose : bool
        If print addition information
    
    date : [datetime]
        Start and End dates in a 2-element list
    '''
    var_list = [
        '10m_u_component_of_wind',
        '10m_v_component_of_wind',
        '2m_dewpoint_temperature',
        '2m_temperature',
        'boundary_layer_height',
        'friction_velocity',
        'land_sea_mask',
        'mean_sea_level_pressure',
        'geopotential',
        'soil_type',
        'surface_pressure',
        'total_precipitation',
        'volumetric_soil_water_layer_1'
        ]        

    def __init__(self, args):
        super().__init__(args)
    
    def _getParams(self):
        '''Define the config dictionary required by CDS'''
        params = super()._getParams()

        date1 = self.date[0].strftime("%Y-%m-%d")
        date2 = self.date[1].strftime("%Y-%m-%d")
        time  = [f"{h:02d}:00" for h in range(0,24,self.step)]

        #Parameters
        params['product_type']   = 'reanalysis'
        params['time']           = time
        params['date']           =  f"{date1}/{date2}"
        params['variable']       = self.var_list

        return params

    def _getDatabase(self):
        '''Define the database required by CDS'''
        if self._backExt():
            database = 'reanalysis-era5-single-levels-preliminary-back-extension'
        else:
            database = 'reanalysis-era5-single-levels'
        return database

    def _getFname(self):
        '''Define the output filename'''
        date1 = self.date[0].strftime("%Y%m%d")
        date2 = self.date[1].strftime("%Y%m%d")
        fname = f"era5.sfc.{date1}-{date2}.nc" 
        return fname

class CARRA(ECMWF):
    '''
    CARRA object to request and download CARRA 
    reanalysis files from ECMWF using the 
    Climate Data Store (CDS) Application 
    Program Interface (API).

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined
    '''

    attrs = {
         'step':       'int',
         'verbose':    'bool',
         'date':       'str',
        }

    def __init__(self, args):
        super().__init__(args)

    def _getParams(self):
        '''Define the config dictionary required by CDS'''
        params = super()._getParams()

        date1 = self.date[0].strftime("%Y-%m-%d")
        date2 = self.date[1].strftime("%Y-%m-%d")
        time  = [f"{h:02d}:00" for h in range(0,24,self.step)]

        #Parameters
        params['format']         = 'grib'
        params['domain']         = 'west_domain'
        params['product_type']   = 'analysis'
        params['time']           = time
        params['date']           = f"{date1}/{date2}"

        return params

    @Config.step.setter
    def step(self,value):
        super(CARRA,type(self)).step.fset(self,value)
        if self._step%3 != 0:
            raise ValueError("Argument step should be a multiple of 3")

class CARRApl(CARRA):
    '''
    CARRApl object to request and download CARRA 
    reanalysis (pressure levels) files from ECMWF 
    using the Climate Data Store (CDS) Application 
    Program Interface (API).

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined

    Attributes
    ----------
    step : int
        Time step in hours
    
    verbose : bool
        If print addition information
    
    date : [datetime]
        Start and End dates in a 2-element list
    '''
    var_list = [
        'geopotential',
        'relative_humidity',
        'temperature',
        'u_component_of_wind',
        'v_component_of_wind',
        'geometric_vertical_velocity',
        ]

    lev_list = [
        '1','2','3','5','7',
        '10','20','30','50','70',
        '100','125','150','175',
        '200','225','250',
        '300','350',
        '400','450',
        '500','550',
        '600','650',
        '700','750','775',
        '800','825','850','875',
        '900','925','950','975',
        '1000'
        ]

    def __init__(self, args):
        super().__init__(args)

    def _getParams(self):
        '''Define the config dictionary required by CDS'''
        params = super()._getParams()

        #Parameters
        params['variable']       = self.var_list
        params['pressure_level'] = self.lev_list

        return params

    def _getDatabase(self):
        '''Define the database required by CDS'''
        database = 'reanalysis-carra-pressure-levels'
        return database

    def _getFname(self):
        '''Define the output filename'''
        date1 = self.date[0].strftime("%Y%m%d")
        date2 = self.date[1].strftime("%Y%m%d")
        fname = f"carra.pl.{date1}-{date2}.grib" 
        return fname

class CARRAsfc(CARRA):
    '''
    CARRAsfc object to request and download CARRA 
    reanalysis (surface level) files from ECMWF 
    using the Climate Data Store (CDS) Application 
    Program Interface (API).

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined

    Attributes
    ----------
    step : int
        Time step in hours
    
    verbose : bool
        If print addition information
    
    date : [datetime]
        Start and End dates in a 2-element list
    '''
    var_list = [
        '10m_u_component_of_wind',
        '10m_v_component_of_wind',
        '2m_relative_humidity',
        '2m_temperature',
        'land_sea_mask',
        'orography',
        'surface_pressure',
        'surface_roughness',
        ]

    def __init__(self, args):
        super().__init__(args)

    def _getParams(self):
        '''Define the config dictionary required by CDS'''
        params = super()._getParams()

        #Parameters
        params['variable']   = self.var_list
        params['level_type'] = 'surface_or_atmosphere'

        return params

    def _getDatabase(self):
        '''Define the database required by CDS'''
        database = 'reanalysis-carra-single-levels'
        return database

    def _getFname(self):
        '''Define the output filename'''
        date1 = self.date[0].strftime("%Y%m%d")
        date2 = self.date[1].strftime("%Y%m%d")
        fname = f"carra.sfc.{date1}-{date2}.grib" 
        return fname

