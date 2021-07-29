import cdsapi
import warnings

class ERA5:
    database     = ""
    params       = { 'format': 'netcdf', 
                     'area'  : '', 
                     'grid'  : '',
                    }

    def __init__(self, args):
        #time arguments
        if args.date_start>args.date_end:
            warnings.warn("date_start greater than date_start. Swaping dates")
            self.date_start, self.date_end = args.date_end, args.date_start
        else:
            self.date_start, self.date_end = args.date_start, args.date_end
        self.step   = args.step

        #lat arguments
        self.latmin = args.latmin
        self.latmax = args.latmax

        #lon arguments
        self.lonmin = args.lonmin
        self.lonmax = args.lonmax

        #western longitudes must be given as negative numbers
        if self.lonmin>=180.: self.lonmin - 360.
        if self.lonmax>=180.: self.lonmax - 360.

        #spatial resolution
        self.res    = args.res

        #output file
        self.output = args.output

        #verbose option
        self.verbose = args.verbose

        self.params['grid'] = "{res}/{res}".format(res=self.res)
        #North/West/South/East
        self.params['area'] = "{latmax}/{lonmin}/{latmin}/{lonmax}".format(lonmin=self.lonmin,
                                                                           lonmax=self.lonmax,
                                                                           latmin=self.latmin,
                                                                           latmax=self.latmax)

        #Check if extended dataset is required
        if self.date_start.year<1979 and self.date_end.year<1979:
            warnings.warn("Requesting ERA5 back extension 1950-1978 (Preliminary version)")
            self.back_extension = True
        else:
            self.back_extension = False

    def retrieve(self):
        if self.verbose:
            print(self.params)
        c = cdsapi.Client()
        c.retrieve(self.database,self.params,self.output)

class ERA5ml(ERA5):
    def __init__(self, args):
        super().__init__(args)

        hr_list = ["{:02d}".format(i) for i in range(0,24,args.step)]

        if self.back_extension:
            self.database = 'reanalysis-era5-complete-preliminary-back-extension'
        else:
            self.database = 'reanalysis-era5-complete'

        #Parameters
        self.params['class']    = 'ea'
        self.params['expver']   = '1'
        self.params['stream']   = 'oper'
        self.params['type']     = 'an'
        self.params['time']     = "/".join(hr_list)
        self.params['date']     = "{date1}/to/{date2}".format(date1=self.date_start.strftime("%Y-%m-%d"),
                                                              date2=self.date_end.strftime("%Y-%m-%d"))
        self.params['levtype']  = 'ml'
        self.params['param']    = '129/130/131/132/133/135/152'
        self.params['levelist'] = '1/to/137'

class ERA5pl(ERA5):
    def __init__(self, args):
        super().__init__(args)

        if self.back_extension:
            self.database = 'reanalysis-era5-pressure-levels-preliminary-back-extension'
        else:
            self.database = 'reanalysis-era5-pressure-levels'

        #Parameters
        self.params['product_type']   = 'reanalysis'
        self.params['time']           = ["{hour:02d}:00".format(hour=i) for i in range(0,24,args.step)]
        self.params['date']           =  "{date1}/{date2}".format(date1=self.date_start.strftime("%Y-%m-%d"),
                                                                  date2=self.date_end.strftime("%Y-%m-%d"))
        self.params['variable']       = [ 'geopotential',
                                          'specific_humidity',
                                          'temperature',
                                          'u_component_of_wind',
                                          'v_component_of_wind',
                                          'vertical_velocity'
                                         ]
        self.params['pressure_level'] = [ '1','2','3','5','7',
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

class ERA5sfc(ERA5):
    def __init__(self, args):
        super().__init__(args)

        if self.back_extension:
            self.database = 'reanalysis-era5-single-levels-preliminary-back-extension'
        else:
            self.database = 'reanalysis-era5-single-levels'

        #Parameters
        self.params['product_type']   = 'reanalysis'
        self.params['time']           = ["{hour:02d}:00".format(hour=i) for i in range(0,24,args.step)]
        self.params['date']           =  "{date1}/{date2}".format(date1=self.date_start.strftime("%Y-%m-%d"),
                                                                  date2=self.date_end.strftime("%Y-%m-%d"))
        self.params['variable']       = [ '10m_u_component_of_wind',
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

