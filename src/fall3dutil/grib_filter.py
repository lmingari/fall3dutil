from .configuration import Config
import requests
from requests.exceptions import HTTPError

class GribFilter(Config):
    '''
    Base object to download Weather GRIB 
    Files from NOMADS using grib filter

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

    def save_data(self):
        for fname, URL in self._fnames():
            if self.verbose: print(f"Saving file: {fname}")
            try:
                self._downloadFile(URL,fname)
            except HTTPError as e:
                msg = f"{e}\n"
                msg += "Cannot access the URL. Check configuration!"
                raise Exception(msg)

    def _downloadFile(self,url,local_filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()

class GFS(GribFilter):
    '''
    GFS object to download GFS Weather GRIB 
    Files from NOMADS using grib filter

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

    time : [int]
        Time range for forecast hours
    
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
        Start date in first element list
    '''

    attrs = {
         'lon':        'float2',
         'lat':        'float2',
         'time':       'int2',
         'res':        'float',
         'cycle':      'int',
         'step':       'int',
         'verbose':    'bool',
         'server':     'str',
         'date':       'str',
        }

    var_list = [ "HPBL", 
                 "PRATE",
                 "LAND",
                 "PRES",
                 "HGT",
                 "RH",
                 "TMP",
                 "UGRD",
                 "VGRD",
                 "VVEL",
                 "SFCR",
                 "SOILW",
                ]

    url_conf = {
            0.25: {'res': "0p25", 'ext': "pgrb2",     'dataset': "gfs", 'datadir': "atmos"},
            0.5:  {'res': "0p50", 'ext': "pgrb2full", 'dataset': "gfs", 'datadir': "atmos"},
            1.0:  {'res': "1p00", 'ext': "pgrb2",     'dataset': "gfs", 'datadir': "atmos"},
            }

    def __init__(self, args):
        super().__init__(args)

    def _getURL(self,fname):
        URL = "https://{server}/cgi-bin/filter_{dataset}_{res}.pl?".format(
                server  = self.server,
                dataset = self.url_conf[self.res]['dataset'],
                res     = self.url_conf[self.res]['res'])

        #Append directory
        URL += "dir=%2F{dataset}.{date}%2F{cycle:02d}%2F{datadir}".format(
                dataset = self.url_conf[self.res]['dataset'],
                date    = self.date[0].strftime("%Y%m%d"),
                cycle   = self.cycle,
                datadir = self.url_conf[self.res]['datadir'])

        #Append filename
        URL += "&file={fname}".format(fname=fname)

        #Append level list
        URL += "&all_lev=on"

        #Append variable list
        URL += "".join(["&var_"+item+"=on" for item in self.var_list])

        #Append subste information
        URL += "&subregion="
        URL += "&leftlon={lonmin}&rightlon={lonmax}".format(
                lonmin = self.lon[0],
                lonmax = self.lon[1], )
        URL += "&toplat={latmax}&bottomlat={latmin}".format(
                latmin = self.lat[0],
                latmax = self.lat[1] )

        return URL

    def _getFname(self,time):
        fname  = "{dataset}.t{cycle:02d}z.{ext}.{res}.f{time:03d}".format(
                dataset = self.url_conf[self.res]['dataset'],
                cycle   = self.cycle,
                ext     = self.url_conf[self.res]['ext'],
                res     = self.url_conf[self.res]['res'],
                time    = time)
        return fname

    def _fnames(self):
        for it in range(self.time[0],self.time[1]+1,self.step):
            fname = self._getFname(it)
            URL   = self._getURL(fname)
            yield (fname, URL)

class GEFS(GribFilter):
    '''
    GEFS object to download GEFS Weather GRIB 
    Files from NOMADS using grib filter

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

    time : [int]
        Time range for forecast hours

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
        Start date in first element list
    '''

    var_list_a = [ "PRES",
                   "HGT",
                   "RH",
                   "TMP",
                   "UGRD",
                   "VGRD",
                   "VVEL",
                ]

    var_list_b = [ "PRATE",
                   "LAND",
                   "SFCR",
                   "SOILW",
                  ]


    url_conf = {
            0.5:  {'res': "0p50", 'ext': "pgrb2", 'dataset': "gefs", 'datadir': "atmos"},
            0.25: {'res': "0p25", 'ext': "pgrb2", 'dataset': "gefs", 'datadir': "atmos"},
            }

    def __init__(self, args):
        super().__init__(args)

    def _getURL(self,fname,dataid):
        URL = "https://{server}/cgi-bin/filter_{dataset}_{datadir}_{res}.pl?".format(
                server  = self.server,
                dataset = self.url_conf[self.res]['dataset'],
                datadir = self.url_conf[self.res]['datadir'],
                res     = self.url_conf[self.res]['res']+dataid)

        #Append directory
        URL += "dir=%2F{dataset}.{date}%2F{cycle:02d}%2F{datadir}%2F{ext}{res}".format(
                dataset = self.url_conf[self.res]['dataset'],
                date    = self.date[0].strftime("%Y%m%d"),
                cycle   = self.cycle,
                datadir = self.url_conf[self.res]['datadir'],
                ext     = self.url_conf[self.res]['ext']+dataid,
                res     = self.url_conf[self.res]['res'].replace("0","") )

        #Append filename
        URL += "&file={fname}".format(fname=fname)

        #Append level list
        URL += "&all_lev=on"

        #Append variable list
        var_list = self.var_list_a
        if dataid == 'b': var_list += self.var_list_b
        URL += "".join(["&var_"+item+"=on" for item in var_list])

        #Append crop information
        URL += "&subregion="
        URL += "&leftlon={lonmin}&rightlon={lonmax}".format(
                lonmin = self.lon[0],
                lonmax = self.lon[1], )
        URL += "&toplat={latmax}&bottomlat={latmin}".format(
                latmin = self.lat[0],
                latmax = self.lat[1] )

        return URL

    def _getFname(self,ens,dataid,time):
        fname  = "gep{ens:02d}.t{cycle:02d}z.{ext}.{res}.f{time:03d}".format(
                ens   = ens,
                cycle = self.cycle,
                ext   = self.url_conf[self.res]['ext']+dataid,
                res   = self.url_conf[self.res]['res'],
                time  = time)
        return fname

    def _fnames(self):
        for dataid in ['a','b']:
            for ie in range(self.ens[0],self.ens[1]+1):
                for it in range(self.time[0],self.time[1]+1,self.step):
                    fname = self._getFname(ie,dataid,it)
                    URL   = self._getURL(fname,dataid)
                    yield (fname, URL)

    @Config.step.setter
    def step(self,value):
        super(GEFS,type(self)).step.fset(self,value)
        if self._step%3 != 0:
            raise ValueError("Argument step should be a multiple of 3")

    @Config.time.setter
    def time(self,value):
        super(GEFS,type(self)).time.fset(self,value)
        if self._time[0]%3 != 0:
            raise ValueError("Argument start time should be a multiple of 3")
