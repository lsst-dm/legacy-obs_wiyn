#!/usr/bin/env python

from __future__ import division

import lsst.daf.base as dafBase
import lsst.afw.image as afwImage
import lsst.afw.image.utils as afwImageUtils

from lsst.obs.base import CameraMapper
import lsst.pex.policy as pexPolicy

__all__ = ["WhircMapper"]


class WhircMapper(CameraMapper):
    packageName = 'obs_wiyn'

    def __init__(self, outputRoot=None, **kwargs):
        policyFile = pexPolicy.DefaultPolicyFile(self.packageName, "WhircMapper.paf", "policy")
        policy = pexPolicy.Policy(policyFile)

        CameraMapper.__init__(self, policy, policyFile.getRepositoryPath(), **kwargs)

        afwImageUtils.defineFilter('OPEN', lambdaEff=1750)  # nm
        afwImageUtils.defineFilter('J' , lambdaEff=1250)
        afwImageUtils.defineFilter('H' , lambdaEff=1650)
        afwImageUtils.defineFilter('KS', lambdaEff=2175, alias=['Ks'])

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
        day  = pathId['day']
        ccd  = pathId['obsnum']
        return long('{}{}{}{}'.format(year, mon, day, ccd))

    def bypass_defects(self, datasetType, pythonType, location, dataId):
        """ since we have no defects, return an empty list.  Fix this when defects exist """
        return []

    def bypass_ccdExposureId(self, datasetType, pythonType, location, dataId):
        return self._computeCcdExposureId(dataId)

    def bypass_ccdExposureId_bits(self, datasetType, pythonType, location, dataId):
        return 32 # not really, but this leaves plenty of space for sources

    def _extractDetectorName(self, dataId):
        return "VIRGO1"

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
        mjd  = dataId['mjd']

        exptime = dataId['exptime']

        calib = item.getCalib()
        calib.setExptime(exptime)

        obsMidpoint = dafBase.DateTime(mjd, dafBase.DateTime.MJD, dafBase.DateTime.UTC) + exptime / 2
        calib.setMidTime(obsMidpoint)

    def _setFilter(self, mapping, item, dataId):
        item.setFilter(afwImage.Filter("FILTER1"))
        # FILTER2 is always set to "OPEN"

    def std_dark(self, item, dataId):
        mapping = self.calibrations['dark']
        item = self._standardizeExposure(mapping, item, dataId, filter=False, trimmed=False)
        self._setTimes(mapping, item, dataId)
        return item

    def getKeys(self, datasetType, *args, **kwargs):
        keyDict = super(WhircMapper, self).getKeys(datasetType, *args, **kwargs)
        if datasetType == "raw":
            keyDict['ccd'] = int
        if datasetType == "flat":
            keyDict['ccd'] = int
        return keyDict
