import unittest
import ocgis
from ocgis.conv.meta import XMLMetaConverter


class Test(unittest.TestCase):

    def test_write(self):
        uri = '/usr/local/climate_data/daymet/tmax.nc'
        variable = 'tmax'
        rd = ocgis.RequestDataset(uri,variable)
        ops = ocgis.OcgOperations(dataset=rd)
        conv = XMLMetaConverter(ops)
        import ipdb;ipdb.set_trace()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()