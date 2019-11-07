from datetime import timedelta
import requests

class GribFilter:
    server   = "nomads.ncep.noaa.gov"
    var_list = []
    lev_list = []

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

        #spatial resolution
        self.res    = args.res

        #output file
        self.output = args.output

        #verbose option
        self.verbose = args.verbose

    def save_data(self):
        if self.verbose: print("saving data")
        for it in range(self.it1,self.it2):
            #forecast hour
            fh  = it*self.step
            URL = self._getURL(fh)
            if self.verbose: print("Working for forecast time",fh)
            if self.verbose: print("Opening",URL)
            local_filename = "{fh:03d}-{basename}".format(basename = self.output,
                                                          fh       = fh)
            self._downloadFile(URL,local_filename)

    def _getURL(self,fh):
        if self.res==0.25:
            res = "0p25"
            ext = "pgrb2"
        elif self.res==0.5:
            res = "0p50"
            ext = "pgrb2full"
        elif self.res==1.0:
            res = "1p00"
            ext = "pgrb2"
        URL = "https://{server}/cgi-bin/filter_gfs_{res}.pl".format(server=self.server,res=res)
        #Append filename
        URL = URL + "?file=gfs.t{cycle:02d}z.{ext}.{res}.f{fhhh:03d}".format(cycle = self.cycle,
                                                                             ext   = ext,
                                                                             res   = res, 
                                                                             fhhh  = fh )
        #Append level list
        URL = URL + "".join(["&lev_"+item+"=on" for item in self.lev_list])
        #Append variable list
        URL = URL + "".join(["&var_"+item+"=on" for item in self.var_list])
        #Append subste information
        URL = URL + "&subregion=&leftlon={lonmin}&rightlon={lonmax}&toplat={latmax}&bottomlat={latmin}".format(lonmin = self.lonmin,
                                                                                                               lonmax = self.lonmax,
                                                                                                               latmin = self.latmin,
                                                                                                               latmax = self.latmax )
        #Append
        URL = URL + "&dir=%2Fgfs.{date}%2F{cycle:02d}".format(date  = self.time_ref.strftime("%Y%m%d"),
                                                              cycle = self.cycle)
        return URL

    def _downloadFile(self,url,local_filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()

class GFS(GribFilter):
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

    lev_list = [ 'surface',
                 '2_m_above_ground',
                 '10_m_above_ground',
                 '0-0.1_m_below_ground',
                 '0.4_mb',
                 '1_mb',
                 '2_mb',
                 '3_mb',
                 '5_mb',
                 '7_mb',
                 '10_mb',
                 '15_mb',
                 '20_mb',
                 '30_mb',
                 '40_mb',
                 '50_mb',
                 '70_mb',
                 '100_mb',
                 '150_mb',
                 '200_mb',
                 '250_mb',
                 '300_mb',
                 '350_mb',
                 '400_mb',
                 '450_mb',
                 '500_mb',
                 '550_mb',
                 '600_mb',
                 '650_mb',
                 '700_mb',
                 '750_mb',
                 '800_mb',
                 '850_mb',
                 '900_mb',
                 '925_mb',
                 '950_mb',
                 '975_mb',
                 '1000_mb',
                 ]

    def __init__(self, args):
        super().__init__(args)

        if self.res==0.5:
            self.lev_list += ['125_mb',
                              '175_mb',
                              '225_mb',
                              '275_mb',
                              '325_mb',
                              '375_mb',
                              '425_mb',
                              '475_mb',
                              '525_mb',
                              '575_mb',
                              '625_mb',
                              '675_mb',
                              '725_mb',
                              '775_mb',
                              '825_mb',
                              '875_mb',
                              ]


