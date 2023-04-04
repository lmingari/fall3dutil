from .configuration import Config
import requests

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
        """Server for GFS data"""
        return self._server

    @server.setter
    def server(self,value):
        if value is None:
            self._server = "nomads.ncep.noaa.gov"

    def save_data(self):
        URL_base   = self._getURL()
        for fname in self._fnames():
            URL = URL_base.format(fname=fname)
            if self.verbose: print(f"Saving file: {fname}")
            self._downloadFile(URL,fname)

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
            0.25: {'res': "0p25", 'ext': "pgrb2"},
            0.5:  {'res': "0p50", 'ext': "pgrb2full"},
            1.0:  {'res': "1p00", 'ext': "pgrb2"},
            }

    def __init__(self, args):
        super().__init__(args)

    def _getURL(self):
        URL = "https://{server}/cgi-bin/filter_gfs_{res}.pl".format(
                server = self.server,
                res    = self.url_conf[self.res]['res'])

        #Append filename
        URL += "?file={fname}"

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

        #Append tail
        URL += "&dir=%2Fgfs.{date}%2F{cycle:02d}%2Fatmos".format(
                date  = self.date[0].strftime("%Y%m%d"),
                cycle = self.cycle)

        return URL

    def _getFname(self):
        fname  = "gfs.t{cycle:02d}z.{ext}.{res}.".format(
                cycle = self.cycle,
                ext   = self.url_conf[self.res]['ext'],
                res   = self.url_conf[self.res]['res'],
                )
        fname += "f{time:03d}"
        return fname

    def _fnames(self):
        fname_base = self._getFname()
        for it in range(self.time[0],self.time[1]+1,self.step):
            fname = fname_base.format(time=it)
            yield fname

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
            0.5:  {'res': "0p50", 'ext': "pgrb2a"},
            }

    def __init__(self, args):
        super().__init__(args)

    def _getURL(self):
        URL = "https://{server}/cgi-bin/filter_gefs_atmos_{res}a.pl".format(
                server = self.server,
                res    = self.url_conf[self.res]['res'])

        #Append directory
        URL += "?dir=%2Fgefs.{date}%2F{cycle:02d}%2Fatmos%2F{ext}p5".format(
                date  = self.date[0].strftime("%Y%m%d"),
                cycle = self.cycle,
                ext   = self.url_conf[self.res]['ext'] )

        #Append filename
        URL += "&file={fname}"

        #Append variable list
        URL += "".join(["&var_"+item+"=on" for item in self.var_list])

        #Append level list
        URL += "&all_lev=on"

        #Append crop information
        URL += "&subregion="
        URL += "&leftlon={lonmin}&rightlon={lonmax}".format(
                lonmin = self.lon[0],
                lonmax = self.lon[1], )
        URL += "&toplat={latmax}&bottomlat={latmin}".format(
                latmin = self.lat[0],
                latmax = self.lat[1] )

        return URL

    def _getFname(self):
        fname  = "gep{ens:02d}."
        fname += "t{cycle:02d}z.{ext}.{res}.".format(
                  cycle = self.cycle,
                  ext   = self.url_conf[self.res]['ext'],
                  res   = self.url_conf[self.res]['res'],
                  )
        fname += "f{time:03d}"
        return fname

    def _fnames(self):
        fname_base = self._getFname()
        for ie in range(self.ens[0],self.ens[1]+1):
            for it in range(self.time[0],self.time[1]+1,self.step):
                fname = fname_base.format(time=it,ens=ie)
                yield fname
