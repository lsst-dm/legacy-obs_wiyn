#
# LSST Data Management System
# Copyright 2008-2016 AURA/LSST.
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

from __future__ import absolute_import, division, print_function

import lsst.pipe.base as pipeBase
import lsst.pex.config as pexConfig


class WhircNullIsrConfig(pexConfig.Config):
    doWrite = pexConfig.Field(
        dtype=bool,
        doc="Persist loaded data as a postISRCCD? The default is false, to avoid duplicating data.",
        default=False,
    )
    datasetType = pexConfig.Field(
        dtype=str,
        doc="Dataset type for input data; read by ProcessCcdTask; users will typically leave this alone",
        default="stack",
)

from lsst.ip.isr import IsrTask

class WhircNullIsrTask(pipeBase.Task):
    """!
    \anchor WhircIsrTask_

    \brief Skip ISR processing.  Return stack exposure.

    """
    ConfigClass = WhircNullIsrConfig
    _DefaultName = "isr"

    @pipeBase.timeMethod
    def runDataRef(self, sensorRef, datesetType='stack'):
        """Return the ISRed stack image

        - Process raw exposure in run()
        - Persist the ISR-corrected exposure as "postISRCCD" if config.doWrite is True

        \param[in] sensorRef -- daf.persistence.butlerSubset.ButlerDataRef of the
                                detector data to be processed
        \return a pipeBase.Struct with fields:
        - exposure: the exposure after application of ISR
        """
        self.log.info("Fetch stack image on sensor %s" % (sensorRef.dataId))
        Exposure = sensorRef.get(datasetType)

        return pipeBase.Struct(
            exposure=exposure,
        )
