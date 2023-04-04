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