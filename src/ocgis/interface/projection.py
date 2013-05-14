from warnings import warn
from osgeo.osr import SpatialReference
from ocgis.util.helpers import itersubclasses
from osgeo.ogr import CreateGeometryFromWkb
from shapely.geometry.point import Point
#from osgeo import osr
#from shapely import wkb
import abc


def get_projection(dataset):
    projs = []
    for r in itersubclasses(DatasetSpatialReference):
        try:
            projs.append(r(dataset))
        except NoProjectionFound:
            continue
    if len(projs) == 1:
        ret = projs[0]
    elif len(projs) == 0:
        warn('no projection information found assuming WGS84')
        ret = WGS84()
    else:
        raise(MultipleProjectionsFound)
    return(ret)
    

class NoProjectionFound(Exception):
    pass


class MultipleProjectionsFound(Exception):
    pass


class OcgSpatialReference(object):
    __metaclass__ = abc.ABCMeta
    _build = None
    
    @abc.abstractmethod
    def write_to_rootgrp(self,rootgrp): return(None)
        
    @abc.abstractproperty
    def sr(self): pass
        
    def get_area_km2(self,to_sr,geom):
        if isinstance(geom,Point):
            ret = None
        else:
            geom = CreateGeometryFromWkb(geom.wkb)
            geom.AssignSpatialReference(self.sr)
            geom.TransformTo(to_sr)
            ret = geom.GetArea()*1e-6
        return(ret)
    
#    def project_to_match(self,geoms,in_sr=None):
#        """
#        Args:
#          geoms: A sequence of geometry dictionaries.
#          
#        Returns:
#          A projected copy of the input geometry sequence.
#        """
#        if in_sr is None:
#            in_sr = osr.SpatialReference()
#            in_sr.ImportFromEPSG(4326)
#        
#        ret = [None]*len(geoms)
#        for idx in range(len(geoms)):
#            gc = geoms[idx].copy()
#            geom = CreateGeometryFromWkb(gc['geom'].wkb)
#            geom.AssignSpatialReference(in_sr)
#            geom.TransformTo(self.sr)
#            gc['geom'] = wkb.loads(geom.ExportToWkb())
#            ret[idx] = gc
##            import ipdb;ipdb.set_trace()
##        try:
##            if self._srid == to_sr._srid:
##                ret = geom.wkb
##        except AttributeError:
##            geom = CreateGeometryFromWkb(geom.wkb)
##            geom.AssignSpatialReference(self.sr)
##            geom.TransformTo(to_sr)
##            ret = geom.ExportToWkb()
#        return(ret)
#    
##    def get_sr(self,proj4_str):
##        sr = osr.SpatialReference()
##        sr.ImportFromProj4(proj4_str)
##        return(sr)
    
    
class SridSpatialReference(OcgSpatialReference):
    
    @abc.abstractproperty
    def _srid(self): int
        
    @property
    def sr(self):
        sr = SpatialReference()
        sr.ImportFromEPSG(self._srid)
        return(sr)


class DatasetSpatialReference(OcgSpatialReference):
    
    def __init__(self,dataset):
        self._proj4_str = self._get_proj4_(dataset)
        
    @property
    def sr(self):
        sr = SpatialReference()
        sr.ImportFromProj4(self._proj4_str)
        return(sr)
    
    @abc.abstractmethod
    def _get_proj4_(self,dataset): str
    
    
#class HostetlerProjection(DatasetSpatialReference):
#    
#    def write_to_rootgrp(self):
#        raise(NotImplementedError)
#    
#    def _get_proj4_(self,dataset):
#        try:
#            var = dataset.variables['Lambert_Conformal']
#            proj = ('+proj=lcc +lat_1={lat1} +lat_2={lat2} +lat_0={lat0} '
#                    '+lon_0={lon0} +x_0=0 +y_0=0 +datum=WGS84 '
#                    '+to_meter=1000.0 +no_defs')
#            lat1,lat2 = var.standard_parallel[0],var.standard_parallel[1]
#            lat0 = var.latitude_of_projection_origin
#            lon0 = var.longitude_of_central_meridian
#            proj = proj.format(lat1=lat1,lat2=lat2,lat0=lat0,lon0=lon0)
#            return(proj)
#        except KeyError:
#            raise(NoProjectionFound)
        
        
class LambertConformalConic(DatasetSpatialReference):
    
    def write_to_rootgrp(self,rootgrp,ncmeta):
        try:
            ref = ncmeta['variables']['lambert_conformal_conic']
            lc = rootgrp.createVariable('lambert_conformal_conic',ref['dtype'])
        except KeyError:
            ref = ncmeta['variables']['Lambert_Conformal']
            lc = rootgrp.createVariable('Lambert_Conformal',ref['dtype'])
        for k,v in ref['attrs'].iteritems():
            setattr(lc,k,v)
    
    def _get_proj4_(self,dataset):
        keys = ['lambert_conformal_conic','Lambert_Conformal']
        try:
            for ii,key in enumerate(keys,start=1):
                try:
                    var = dataset.variables[key]
                except KeyError:
                    if ii == len(keys):
                        raise
                    else:
                        continue
            proj = ('+proj=lcc +lat_1={lat1} +lat_2={lat2} +lat_0={lat0} '
                    '+lon_0={lon0} +x_0={false_easting} +y_0={false_northing} +datum=WGS84 '
                    '+units=km +no_defs ')
            lat1,lat2 = var.standard_parallel[0],var.standard_parallel[1]
            lat0 = var.latitude_of_projection_origin
            lon0 = var.longitude_of_central_meridian
            false_easting = var.false_easting
            false_northing = var.false_northing
            proj = proj.format(lat1=lat1,lat2=lat2,lat0=lat0,lon0=lon0,false_easting=false_easting,false_northing=false_northing)
            return(proj)
        except KeyError:
            raise(NoProjectionFound)
        

class NarccapObliqueMercator(DatasetSpatialReference):
    
    def write_to_rootgrp(self,rootgrp,ncmeta):
        ref = ncmeta['variables']['Transverse_Mercator']
        lc = rootgrp.createVariable('Transverse_Mercator',ref['dtype'])
        for k,v in ref['attrs'].iteritems():
            setattr(lc,k,v)
            
    def _get_proj4_(self,dataset):
        try:
            var = dataset.variables['Transverse_Mercator']
            
            proj = ('+proj=omerc +lat_0={lat_0} +lonc={lonc} +k_0={k_0} '
                    '+x_0={false_easting} +y_0={false_northing} +alpha=360')
            
            lat_0 = var.latitude_of_projection_origin
            lonc = var.longitude_of_central_meridian
            k_0 = var.scale_factor_at_central_meridian
            false_easting = var.false_easting
            false_northing = var.false_northing
            
            proj = proj.format(lat_0=lat_0,lonc=lonc,k_0=k_0,false_easting=false_easting,
                               false_northing=false_northing)

            return(proj)
        except KeyError:
            raise(NoProjectionFound)


class PolarStereographic(DatasetSpatialReference):
    
    def write_to_rootgrp(self,rootgrp,ncmeta):
        ref = ncmeta['variables']['polar_stereographic']
        lc = rootgrp.createVariable('polar_stereographic',ref['dtype'])
        for k,v in ref['attrs'].iteritems():
            setattr(lc,k,v)
            
    def _get_proj4_(self,dataset):
        try:
            var = dataset.variables['polar_stereographic']
            proj = ('+proj=stere +lat_ts={latitude_natural} +lat_0={lat_0} +lon_0={longitude_natural} '
                    '+k_0={scale_factor} +x_0={false_easting} +y_0={false_northing}')
            
            false_easting = var.false_easting
            false_northing = var.false_northing
            latitude_natural = var.standard_parallel
            lat_0 = var.latitude_of_projection_origin
            scale_factor = 1.0
            longitude_natural = var.straight_vertical_longitude_from_pole

            proj = proj.format(false_easting=false_easting,false_northing=false_northing,
                    latitude_natural=latitude_natural,lat_0=lat_0,scale_factor=scale_factor,
                    longitude_natural=longitude_natural)

            return(proj)
        except KeyError:
            raise(NoProjectionFound)
        
        
class RotatedPole(DatasetSpatialReference):
    
    def write_to_rootgrp(self,rootgrp,ncmeta):
        ref = ncmeta['variables']['rotated_pole']
        lc = rootgrp.createVariable('rotated_pole',ref['dtype'])
        for k,v in ref['attrs'].iteritems():
            setattr(lc,k,v)
            
    def _get_proj4_(self,dataset):
        try:
            var = dataset.variables['rotated_pole']
            self.grid_north_pole_latitude = var.grid_north_pole_latitude
            self.grid_north_pole_longitude = var.grid_north_pole_longitude
            proj = '+proj=ob_tran +o_proj=latlon +o_lon_p={lon_pole} +o_lat_p={lat_pole} +lon_0=180'
            self._trans_proj = proj.format(lon_pole=self.grid_north_pole_longitude,lat_pole=self.grid_north_pole_latitude)
#            return(proj)
            return(WGS84().sr.ExportToProj4())
        except KeyError:
            raise(NoProjectionFound)
        
        
class WGS84(SridSpatialReference):
    _srid = 4326
    
    def write_to_rootgrp(self,rootgrp):
        pass


class UsNationalEqualArea(SridSpatialReference):
    _srid = 2163
