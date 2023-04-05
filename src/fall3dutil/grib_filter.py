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
    var_list = []

    def __init__(self, args):
        super().__init__(args)
        if self.verbose: self.printInfo()

    @property
    def server(self):
        """Server for nomads"""
        return self._server

    @server.setter
    def server(self,value):
        if value is None:
            self._server = "nomads.ncep.noaa.gov"
        else:
            self._server = value
            
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
    var_list = [ "PRES",
                 "HGT",
                 "RH",
                 "TMP",
                 "UGRD",
                 "VGRD",
                 "VVEL",
                 "SOILW",
                ]

    url_conf = {
            0.5:  {'res': "0p50", 'ext': "pgrb2", 'dataset': "gefs", 'datadir': "atmos"},
            0.25: {'res': "0p25", 'ext': "pgrb2", 'dataset': "gefs", 'datadir': "atmos"},
            }

    def __init__(self, args):
        super().__init__(args)

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
        URL += "".join(["&var_"+item+"=on" for item in self.var_list])

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
