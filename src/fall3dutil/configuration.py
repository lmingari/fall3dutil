from datetime import datetime
from configparser import ConfigParser

def parse_float2(s):
    """Read a 2-list a floats"""
    s_list = s.split()
    n = len(s_list)
    if n==0:
        return None
    elif n==1: 
        s_list *= 2
    return [float(item) for item in s_list[:2]]

def parse_int2(s):
    """Read a 2-list a integers"""
    s_list = s.split()
    s_list = s.split()
    n = len(s_list)
    if n==0:
        return None
    elif n==1: 
        s_list *= 2
    return [int(item) for item in s_list[:2]]

class Config:
    '''
    The Config object contains the attributes 
    required by the fall3dutil classes

    Parameters
    ----------
    arg : Namespace object
        A Namespace object generated using the argparse
        module with the list of required attributes as
        defined in the self.attrs variable.
        In addition, attributes can be read from an
        input configuration file using a ConfigParser 
        object if arg.file if defined

    Attributes
    ----------
    lon : [float]
        Longitudes range

    lat : [float]
        Latitudes range

    time : [int]
        Time range

    ens : [int]
        Ensemble members range
    
    res : float
        Resolution in deg
    
    cycle : int
        Cycle
    
    step : int
        Time step in hours
    
    verbose : bool
        If print addition information
    
    server : str
        URL server

    date : [datetime]
        Dates range
    '''
    attrs = {
         'lon':        'float2',
         'lat':        'float2',
         'time':       'int2',
         'ens':        'int2',
         'res':        'float',
         'cycle':      'int',
         'step':       'int',
         'verbose':    'bool',
         'server':     'str',
         'date':       'str',
        }

    def __init__(self,args):
        fname = getattr(args, 'input', None)
        block = getattr(args, 'block', 'DEFAULT')
        if fname is None:
            #
            # Set attributes from args
            #
            for attribute in self.attrs.keys():
                value = getattr(args, attribute, None)
                setattr(self, attribute, value)
        else:
            #
            # Read configuration file
            #
            config = ConfigParser(inline_comment_prefixes="#",
                                  converters = {
                                      'int2':   parse_int2,
                                      'float2': parse_float2
                                      })
            config.read(fname)
            #
            for attribute, attrType in self.attrs.items():
                #
                # Get value from args
                #
                value = getattr(args, attribute, None)
                #
                # Get from config file if attribute is undefined
                #
                if (value is None) and config.has_option(block,attribute):
                    if attrType == 'bool':
                        value = config.getboolean(block, attribute)
                    elif attrType == 'int':
                        value = config.getint(block, attribute)
                    elif attrType == 'float':
                        value = config.getfloat(block, attribute)
                    elif attrType == 'int2':
                        value = config.getint2(block, attribute)
                    elif attrType == 'float2':
                        value = config.getfloat2(block, attribute)
                    else:
                        value = config.get(block, attribute)
                #
                # Set attribute
                #
                setattr(self, attribute, value)

    def printInfo(self):
        """Print attributes values"""
        print("Using the configuration:")
        print("------------------------")
        for att in self.attrs.keys():
            value=getattr(self,att,None)
            if not value is None:
                print(f"{att}: {value}")
        print("------------------------")

    @property
    def date(self):
        """Start and end dates"""
        return self._date

    @date.setter
    def date(self,value):
        if value is None:
            raise ValueError("Missing mandatory argument: date")
        try:
            self._date = [datetime.strptime(date,"%Y%m%d") for date in 
                          (value.split() if isinstance(value,str) else value)]
        except ValueError:
            raise ValueError("Expected date format: YYYYMMDD")

    @property
    def lat(self):
        """Latitude range"""
        return self._lat

    @lat.setter
    def lat(self,value):
        if value is None:
            raise ValueError("Missing mandatory argument: lat")
        if len(value) == 2:
            if value[0]>=value[1]:
                raise ValueError("Expected latitude range: latmin < latmax")
            for lat in value:
                if lat < -90 or lat > 90:
                    raise ValueError("Latitude out of range")
        else:
            raise ValueError("Expected latitude range: latmin latmax")
        self._lat = value

    @property
    def lon(self):
        """Longitude range"""
        return self._lon

    @lon.setter
    def lon(self,value):
        if value is None:
            raise ValueError("Missing mandatory argument: lon")
        if len(value) == 2:
            if value[0]==value[1]:
                raise ValueError("Expected longitude range")
        else:
            raise ValueError("Expected longitude range: lonmin lonmax")
        self._lon = value

    @property
    def step(self):
        """Time step in hours"""
        return self._step

    @step.setter
    def step(self,value):
        if value is None:
            raise ValueError("Missing mandatory argument: step")
        if value < 1:
            raise ValueError("Expected step>=1")
        self._step = value

    @property
    def res(self):
        """Resolution in degrees"""
        return self._res

    @res.setter
    def res(self,value):
        if value is None:
            raise ValueError("Missing mandatory argument: res")
        if value <= 0:
            raise ValueError("Expected res>0")
        self._res = value

    @property
    def cycle(self):
        """Cycle time"""
        return self._cycle

    @cycle.setter
    def cycle(self,value):
        if value is None:
            raise ValueError("Missing mandatory argument: cycle")
        elif value not in [0,6,12,18]:
            raise ValueError("Wrong value for cycle. Valid cycles: 0,6,12,18")
        else:
            self._cycle = value
    
    @property
    def time(self):
        """Time forecast range in hours"""
        return self._time

    @time.setter
    def time(self,value):
        if value is None:
            raise ValueError("Missing mandatory argument: time")
        if len(value) > 1:
            if value[0]>value[1]:
                raise ValueError("Expected a range for time: tmin < tmax")
            elif value[0]<0 or value[1]<0:
                raise ValueError("Expected positive values for time")
        elif len(value) < 2:
                raise ValueError("Expected a range for time: tmin tmax")
        self._time = value

    @property
    def ens(self):
        """Ensemble member range"""
        return self._ens

    @ens.setter
    def ens(self,value):
        if value is None:
            raise ValueError("Missing mandatory argument: ens")
        if len(value) > 1:
            if value[0]>value[1]:
                raise ValueError("Expected a range for ens: ensmin < ensmax")
            elif value[0]<0 or value[1]<0:
                raise ValueError("Expected positive values for ens")
        elif len(value) < 2:
                raise ValueError("Expected a range for ens: ensmin ensmax")
        self._ens = value

    @property
    def server(self):
        """Server for connection"""
        return self._server

    @server.setter
    def server(self,value):
        if value is None:
            self._server = "nomads.ncep.noaa.gov"
        else:
            self._server = value
