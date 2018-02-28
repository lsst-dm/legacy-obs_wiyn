#
# LSST Data Management System
# Copyright 2016 LSST Corporation.
#
# This product includes software developed by the
# LSST Project (http://www.lsst.org/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the LSST License Statement and
# the GNU General Public License along with this program.  If not,
# see <http://www.lsstcorp.org/LegalNotices/>.
#

from __future__ import division

import os

import lsst.daf.base as dafBase
import lsst.afw.image as afwImage
import lsst.afw.image.utils as afwImageUtils

from lsst.obs.base import CameraMapper, MakeRawVisitInfo
import lsst.daf.persistence as dafPersist

from .whirc import Whirc

__all__ = ["WhircMapper"]


class WhircMakeRawVisitInfo(MakeRawVisitInfo):
    """functor to make a VisitInfo from the FITS header of a raw image."""
    def getDateAvg(self, md, exposureTime):
        """Return date at the middle of the exposure

        @param[in,out] md  metadata, as an lsst.daf.base.PropertyList or PropertySet;
            items that are used are stripped from the metadata
            (except TIMESYS, because it may apply to more than one other keyword).
        @param[in] exposureTime  exposure time (sec)

        Subclasses must override. Here is a typical implementation:
        dateObs = self.popIsoDate(md, "DATE-OBS")
        return self.offsetDate(dateObs, 0.5*exposureTime)
        """
        dateObs = self.popIsoDate(md, "DATE-OBS")
        return self.offsetDate(dateObs, 0.5*exposureTime)

class WhircMapper(CameraMapper):
    """Mapper for WIYN+WHIRC"""

    packageName = 'obs_wiyn'
    MakeRawVisitInfoClass = WhircMakeRawVisitInfo

    def __init__(self, outputRoot=None, **kwargs):
        policyFile = dafPersist.Policy.defaultPolicyFile(
            self.packageName, "WhircMapper.yaml", "policy")
        policy = dafPersist.Policy(policyFile)

        CameraMapper.__init__(self, policy, os.path.dirname(policyFile),
                              **kwargs)

        afwImageUtils.defineFilter('OPEN', lambdaEff=1750)  # nm
        afwImageUtils.defineFilter('J', lambdaEff=1250)
        afwImageUtils.defineFilter('H', lambdaEff=1650)
        afwImageUtils.defineFilter('KS', lambdaEff=2175, alias=['Ks'])

    def _makeCamera(self, policy, repositoryDir):
        """Make a camera (instance of lsst.afw.cameraGeom.Camera)
        describing the camera geometry.

        Parameters
        ----------
        policy : anything - unused
            Unused

        repositoryDir : anything - unused
            Unused

        Returns
        -------
        camera : `lsst.afw.cameraGeom.Camera`
            The camera object
        """
        return Whirc()

    def _defectLookup(self, dataId, ccdSerial):
        """Find the defects for a given CCD.
        @param dataId (dict) Dataset identifier
        @param ccdSerial (string) CCD serial number
        @return (string) path to the defects file or None if not available
        """
        return None  # XXX FIXME

    def _computeCcdExposureId(self, dataId):
        """Compute the 64-bit (long) identifier for a CCD exposure.

        @param dataId (dict) Data identifier with visit, ccd
        """
        pathId = self._transformId(dataId)
        # I find it easiest to think about creating a decimal string
        template = '{year:04d}{month:02d}{day:02d}{expnum:06d}'
        # and then converting it to an int:
        return int(template.format(**pathId))

    def bypass_ccdExposureId(self, datasetType, pythonType, location, dataId):
        return self._computeCcdExposureId(dataId)

    def bypass_ccdExposureId_bits(self, datasetType, pythonType, location, dataId):
        return 32  # not really, but this leaves plenty of space for sources

    def _extractDetectorName(self, dataId):
        return "VIRGO1"

    def _computeStackExposureId(self, dataId):
        """Compute the 64-bit (long) identifier for a Stack exposure.

        @param dataId (dict) Data identifier with stack, patch, filter
        """
        nPatches = 1000000
        return (int(dataId["stack"]) * nPatches + int(dataId["patch"]))

    def bypass_stackExposureId(self, datasetType, pythonType, location, dataId):
        return self._computeStackExposureId(dataId)

    def bypass_stackExposureId_bits(self, datasetType, pythonType, location, dataId):
        return 32  # not really, but this leaves plenty of space for sources

    def _setTimes(self, mapping, item, dataId):
        """Set the exposure time and exposure midpoint in the calib object in an Exposure.

        @param mapping (lsst.daf.butlerUtils.Mapping)
        @param[in,out] item (lsst.afw.image.Exposure)
        @param dataId (dict) Dataset identifier
        """
        mjd = dataId['mjd']

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
