import unittest
import ocgis
from ocgis.conv.meta import XMLMetaConverter
import xml.etree.ElementTree as ET
import tempfile
import os.path


class Test(unittest.TestCase):
    
    def write_to_disk(self,rows,outname,outdir=None):
        if outdir is None:
            outdir = tempfile.gettempdir()
        with open(os.path.join(outdir,outname),'w') as f:
            f.write(ET.tostring(rows))

    def test_write(self):
        uri = '/usr/local/climate_data/daymet/tmax.nc'
        variable = 'tmax'
        rd = ocgis.RequestDataset(uri,variable)
        ops = ocgis.OcgOperations(dataset=rd)
        conv = XMLMetaConverter(ops)
        rows = conv.get_rows()
    
    def test_write_calc(self):
        uri = '/usr/local/climate_data/daymet/tmax.nc'
        variable = 'tmax'
        rd = ocgis.RequestDataset(uri,variable)
        ops = ocgis.OcgOperations(dataset=rd,calc=[{'func':'mean','name':'my_mean'},
                                                   {'func':'between','kwds':{'upper':5,'lower':10},'name':'between_5_10'}])
        conv = XMLMetaConverter(ops)
        rows = conv.get_rows()
        self.write_to_disk(rows,'ocgis_xml_meta_example.xml')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()