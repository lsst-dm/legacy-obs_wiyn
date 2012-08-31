#!/usr/bin/env python

import os
import pwd

import lsst.daf.base as dafBase
import lsst.afw.geom as afwGeom
import lsst.afw.coord as afwCoord
import lsst.afw.image as afwImage
import lsst.afw.image.utils as afwImageUtils

from lsst.daf.butlerUtils import CameraMapper, exposureFromImage
import lsst.pex.policy as pexPolicy

class WhircMapper(CameraMapper):
    def __init__(self, outputRoot=None, **kwargs):
        policyFile = pexPolicy.DefaultPolicyFile("obs_wiyn", "WhircMapper.paf", "policy")
        policy = pexPolicy.Policy(policyFile)
#        print policyFile.getRepositoryPath()
        super(WhircMapper, self).__init__(policy, policyFile.getRepositoryPath(), **kwargs)

        afwImageUtils.defineFilter('OPEN', lambdaEff=650)

    def _defectLookup(self, dataId, ccdSerial):
        """Find the defects for a given CCD.
        @param dataId (dict) Dataset identifier
        @param ccdSerial (string) CCD serial number
        @return (string) path to the defects file or None if not available
        """
        return None # XXX FIXME

    def _computeCcdExposureId(self, dataId):
        """Compute the 64-bit (long) identifier for a CCD exposure.

        @param dataId (dict) Data identifier with visit, ccd
        """
        pathId = self._transformId(dataId)
        year = pathId['year']
        mon  = pathId['month']
        sod  = pathId['day']
        ccd  = pathId['obsnum']
        return 0 # XXX FIXME

    def bypass_ccdExposureId(self, datasetType, pythonType, location, dataId):
        return self._computeCcdExposureId(dataId)

    def bypass_ccdExposureId_bits(self, datasetType, pythonType, location, dataId):
        return 32 # not really, but this leaves plenty of space for sources

    def _computeStackExposureId(self, dataId):
        """Compute the 64-bit (long) identifier for a Stack exposure.

        @param dataId (dict) Data identifier with stack, patch, filter
        """
        nPatches = 1000000
        return (long(dataId["stack"]) * nPatches + long(dataId["patch"]))

    def bypass_stackExposureId(self, datasetType, pythonType, location, dataId):
        return self._computeStackExposureId(dataId)

    def bypass_stackExposureId_bits(self, datasetType, pythonType, location, dataId):
        return 32 # not really, but this leaves plenty of space for sources

    def _setTimes(self, mapping, item, dataId):
        """Set the exposure time and exposure midpoint in the calib object in an Exposure.

        @param mapping (lsst.daf.butlerUtils.Mapping)
        @param[in,out] item (lsst.afw.image.Exposure)
        @param dataId (dict) Dataset identifier
        """

        year = dataId['year']
        mon  = dataId['month']
        day  = dataId['day']
        frac = dataId['frac']

        exptime = 1.0 # XXX FIXME

        calib = item.getCalib()
        calib.setExptime(exptime)

        mjd = 51544.0 + int((year - 2000) * 365.25) + doy + frac/10**6 + exptime / 2.0
        obsMidpoint = dafBase.DateTime(mjd, dafBase.DateTime.MJD, dafBase.DateTime.UTC)
        calib.setMidTime(obsMidpoint)

    def _setFilter(self, mapping, item, dataId):
        item.setFilter(afwImage.Filter("OPEN"))

    def bypass_raw(self, datasetType, pythonType, location, dataId):
        ccd = dataId['ccd']
        x, y = 1, 1
        xSize, ySize = 2048, 2048
    
        filename = location.getLocations()[0]
        bbox = afwGeom.Box2I(afwGeom.Point2I(x * xSize, y * ySize), afwGeom.Extent2I(xSize, ySize))
        image = afwImage.DecoratedImageF(filename, hdu, bbox)
        exp = exposureFromImage(image)
        del image

        md = exp.getMetadata()
        md.add("EXPTIME", 1.0)
        md.add("FILTER", "OPEN")

        return self._standardizeExposure(self.exposures['raw'], exp, dataId, filter=True, trimmed=False)

    def std_dark(self, item, dataId):
        mapping = self.calibrations['dark']
        item = self._standardizeExposure(mapping, item, dataId, filter=False, trimmed=False)
        self._setTimes(mapping, item, dataId)
        return item

    def getKeys(self, datasetType, *args, **kwargs):
        keyDict = super(WhircMapper, self).getKeys(datasetType, *args, **kwargs)
        if datasetType == "raw":
            keyDict['ccd'] = int
        return keyDict
