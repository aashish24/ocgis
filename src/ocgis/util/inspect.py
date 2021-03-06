import netCDF4 as nc
from ocgis.interface.ncmeta import NcMetadata
from ocgis.interface.nc.dataset import NcDataset


class Inspect(object):
    """
    Inspect a local or remote dataset returning a printout similar to `ncdump`_.
    
    >>> from ocgis import Inspect
    ...
    >>> # Just do an dataset attribute dump.
    >>> ip = Inspect('/my/local/dataset')
    >>> print(ip)
    ...
    >>> # Get variable-specific info.
    >>> ip = Inspect('/my/local/dataset',variable='tas')
    >>> print(ip)
    
    :param uri: Absolute path to data's location.
    :type uri: str
    :param variable: Specific variable to inspect.
    :type variable: str
    :param interface_overload: Overloads for autodiscover.
    :type interface_overload: dict
    
    .. _ncdump: http://www.unidata.ucar.edu/software/netcdf/docs/netcdf/ncdump.html
    """
    
    def __init__(self,uri,variable=None,interface_overload={}):
        self.uri = uri
        self.variable = variable
        if self.variable is None:
            try:
                self.ds = None
                rootgrp = nc.Dataset(uri)
                self.meta = NcMetadata(rootgrp)
            finally:
                rootgrp.close()
        else:
            from ocgis.api.request import RequestDataset
            kwds = {'uri':uri,'variable':variable}
            kwds.update(interface_overload)
            rd = RequestDataset(**kwds)
            self.ds = NcDataset(request_dataset=rd)
            self.meta = self.ds.metadata
        
    def __repr__(self):
        msg = ''
        if self.variable is None:
            lines = self.get_report_no_variable()
        else:
            lines = self.get_report()
        for line in lines:
            msg += line + '\n'
        return(msg)
        
    @property
    def _t(self):
        return(self.ds.temporal)
    @property
    def _s(self):
        return(self.ds.spatial)
    @property
    def _l(self):
        return(self.ds.level)
        
    def get_temporal_report(self):
        start_date = self._t.value.min()
        end_date = self._t.value.max()
        res = int(self._t.resolution)
        n = len(self._t.value)
        calendar = self._t.calendar
        units = self._t.units
        
        lines = []
        lines.append('       Start Date = {0}'.format(start_date))
        lines.append('         End Date = {0}'.format(end_date))
        lines.append('         Calendar = {0}'.format(calendar))
        lines.append('            Units = {0}'.format(units))
        lines.append('Resolution (Days) = {0}'.format(res))
        lines.append('            Count = {0}'.format(n))
        
        ## append information on bounds
        if self._t.bounds is not None:
            has_bounds = True
        else:
            has_bounds = False
        lines.append('       Has Bounds = {0}'.format(has_bounds))
        
        return(lines)
    
    def get_spatial_report(self):
        res = self._s.grid.resolution
        extent = self._s.grid.extent
        itype = self._s.vector.__class__.__name__
        projection = self.ds.spatial.projection
        
        lines = []
        lines.append('Spatial Reference = {0}'.format(projection.__class__.__name__))
        lines.append('     Proj4 String = {0}'.format(projection.sr.ExportToProj4()))
        lines.append('           Extent = {0}'.format(extent))
        lines.append('   Interface Type = {0}'.format(itype))
        lines.append('       Resolution = {0}'.format(res))
        lines.append('            Count = {0}'.format(self._s.grid.uid.reshape(-1).shape[0]))
        
        return(lines)
    
    def get_level_report(self):
        if self._l is None:
            lines = ['No level dimension found.']
        else:
            lines = []
            lines.append('Level Variable = {0}'.format(self._l.name))
            lines.append('         Count = {0}'.format(self._l.value.shape[0]))
            
            ## append information on bounds
            if self._l.bounds is not None:
                has_bounds = True
            else:
                has_bounds = False
            lines.append('    Has Bounds = {0}'.format(has_bounds))
            
        return(lines)
    
    def get_dump_report(self):
        return(self.meta._get_lines_())
    
    def get_report_no_variable(self):
        lines = ['','URI = {0}'.format(self.uri)]
        lines.append('VARIABLE = {0}'.format(self.variable))
        lines.append('')
        lines += self.get_dump_report()
        return(lines)
    
    def get_report(self):
        mp = [
              {'=== Temporal =============':self.get_temporal_report},
              {'=== Spatial ==============':self.get_spatial_report},
              {'=== Level ================':self.get_level_report},
              {'=== Dump =================':self.get_dump_report}
              ]
        
        lines = ['','URI = {0}'.format(self.uri)]
        lines.append('VARIABLE = {0}'.format(self.variable))
        lines.append('')
        for dct in mp:
            for key,value in dct.iteritems():
                lines.append(key)
                lines.append('')
                for line in value():
                    lines.append(line)
            lines.append('')
        
        return(lines)