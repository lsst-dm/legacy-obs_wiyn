# 
# LSST Data Management System
# Copyright 2014 LSST Corporation.
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
import numpy
import lsst.afw.cameraGeom as cameraGeom
import lsst.afw.geom as afwGeom
from lsst.afw.table import AmpInfoCatalog, AmpInfoTable, LL
from lsst.afw.cameraGeom.cameraFactory import makeDetector

class Whirc(cameraGeom.Camera):
    """The WHIRC Camera

    There is one detector with name "VIRGO0"

    Standard keys are:
    ccd: ccd name: always VIRGO0
    visit: exposure number; this will be provided by the DAQ
    """
    gain = {0: 3.4}  # What we're using from Kotulla's reduce.py
    readNoise = {0: 10}  # Completely made up

    def __init__(self):
        """Construct a TestCamera
        """
        plateScale = afwGeom.Angle(5, afwGeom.arcseconds) # plate scale, in angle on sky/pixel
        # 0.1 "/pixel
        # 20 um/pixel = 0.020 mm / pixel
        # 0.1 "/pixel / 0.020 mm/pixel = 5 "/mm
        radialDistortion = 0. # radial distortion in mm/rad^2
        radialCoeff = numpy.array((0.0, 1.0, 0.0, radialDistortion)) / plateScale.asRadians()
        focalPlaneToPupil = afwGeom.RadialXYTransform(radialCoeff)
        pupilToFocalPlane = afwGeom.InvertedXYTransform(focalPlaneToPupil)
        cameraTransformMap = cameraGeom.CameraTransformMap(cameraGeom.FOCAL_PLANE,
            {cameraGeom.PUPIL: pupilToFocalPlane})
        detectorList = self._makeDetectorList(pupilToFocalPlane, plateScale)
        cameraGeom.Camera.__init__(self, "whirc", detectorList, cameraTransformMap)

    def _makeDetectorList(self, focalPlaneToPupil, plateScale):
        """Make a list of detectors

        @param[in] focalPlaneToPupil  lsst.afw.geom.XYTransform from FOCAL_PLANE to PUPIL coordinates
        @param[in] plateScale  plate scale, in angle on sky/mm
        @return a list of detectors (lsst.afw.cameraGeom.Detector)
        """
        detectorList = []
        detectorConfigList = self._makeDetectorConfigList()
        for detectorConfig in detectorConfigList:
            ampInfoCatalog = self._makeAmpInfoCatalog()
            detector = makeDetector(detectorConfig, ampInfoCatalog, focalPlaneToPupil,
                plateScale.asArcseconds())
            detectorList.append(detector)
        return detectorList

    def _makeDetectorConfigList(self):
        """Make a list of detector configs

        @return a list of detector configs (lsst.afw.cameraGeom.DetectorConfig)
        """
        # There is only a single detector assumed perfectly centered and aligned.
        detector0Config = cameraGeom.DetectorConfig()
        detector0Config.name = 'VIRGO0'
        detector0Config.id = 0
        detector0Config.serial = 'abcd1234'
        detector0Config.detectorType = 0
        # This is the orientation we need to put the serial direciton along the x-axis
        detector0Config.bbox_x0 = 0
        detector0Config.bbox_x1 = 2143
        detector0Config.bbox_y0 = 0
        detector0Config.bbox_y1 = 2049
        detector0Config.pixelSize_x = 0.02 # in mm
        detector0Config.pixelSize_y = 0.02 # in mm
        detector0Config.transformDict.nativeSys = 'Pixels'
        detector0Config.transformDict.transforms = None
        detector0Config.refpos_x = 1023.5
        detector0Config.refpos_y = 1023.5
        detector0Config.offset_x = 0.0
        detector0Config.offset_y = 0.0
        detector0Config.transposeDetector = False
        detector0Config.pitchDeg = 0.0
        detector0Config.yawDeg = 0.0 # this is where chip rotation goes in.
        detector0Config.rollDeg = 0.0
        return [detector0Config]

    def _makeAmpInfoCatalog(self):
        """Construct an amplifier info catalog
        """
        # Much of this will need to be filled in when we know it.
        xDataExtent = 2048 # trimmed
        yDataExtent = 2048

        extended = 10 # extended register
        h_overscan = 96 # number of overscan in x
        v_overscan = 2 # number of overscan in y

        xRawExtent = extended + h_overscan + xDataExtent
        yRawExtent = v_overscan + yDataExtent # no prescan in vertical

        saturation = 65535
        # Linearity correction is still under discussion, so this is a placeholder.
        linearityType = "PROPORTIONAL"
        linearityThreshold = 0
        linearityMax = saturation
        linearityCoeffs = [linearityThreshold, linearityMax]

        schema = AmpInfoTable.makeMinimalSchema()

        linThreshKey = schema.addField('linearityThreshold', type=float)
        linMaxKey = schema.addField('linearityMaximum', type=float)
        linUnitsKey = schema.addField('linearityUnits', type=str, size=9)
        # end placeholder
        self.ampInfoDict = {}
        ampCatalog = AmpInfoCatalog(schema)
        for ampY in (0):
            for ampX in (0):
                record = ampCatalog.addNew()
                record.setName("%d%d" % (ampX, ampY))
                
                if bool(ampY):
                    record.setBBox(afwGeom.Box2I(
                            afwGeom.Point2I(ampX * xDataExtent, ampY * yDataExtent),
                                            afwGeom.Extent2I(xDataExtent, yDataExtent),
                    ))
                else:
                    record.setBBox(afwGeom.Box2I(
                            afwGeom.Point2I((7-ampX) * xDataExtent, ampY * yDataExtent),
                                            afwGeom.Extent2I(xDataExtent, yDataExtent),
                    ))

                readCorner = LL # in raw frames; always LL because raws are in amp coords
                # bias region
                x0Bias = extended + xDataExtent
                y0Data = 0
                x0Data = extended

                record.setRawBBox(afwGeom.Box2I(
                    afwGeom.Point2I(0, 0),
                    afwGeom.Extent2I(xRawExtent, yRawExtent),
                ))
                record.setRawDataBBox(afwGeom.Box2I(
                    afwGeom.Point2I(x0Data, y0Data),
                    afwGeom.Extent2I(xDataExtent, yDataExtent),
                ))
                record.setRawHorizontalOverscanBBox(afwGeom.Box2I(
                    afwGeom.Point2I(x0Bias, y0Data),
                    afwGeom.Extent2I(h_overscan, yDataExtent),
                ))
                record.setRawVerticalOverscanBBox(afwGeom.Box2I(
                    afwGeom.Point2I(x0Data, y0Data+yDataExtent),
                    afwGeom.Extent2I(xDataExtent, v_overscan),
                ))
                record.setRawXYOffset(afwGeom.Extent2I(ampX*xRawExtent, ampY*yRawExtent))
                record.setReadoutCorner(readCorner)
                record.setGain(self.gain[(ampX, ampY)])
                record.setReadNoise(self.readNoise[(ampX, ampY)])
                record.setSaturation(saturation)
                record.setHasRawInfo(True)
                record.setRawFlipX(bool(ampY))
                # flip data when assembling if in top of chip
                record.setRawFlipY(bool(ampY))
                record.setRawPrescanBBox(afwGeom.Box2I())
                # linearity placeholder stuff
                record.setLinearityCoeffs([float(val) for val in linearityCoeffs])
                record.setLinearityType(linearityType)
                record.set(linThreshKey, float(linearityThreshold))
                record.set(linMaxKey, float(linearityMax))
                record.set(linUnitsKey, "DN")
        return ampCatalog
