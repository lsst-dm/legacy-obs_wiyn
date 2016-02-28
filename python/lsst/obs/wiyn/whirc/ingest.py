from __future__ import print_function
import os
from lsst.pipe.tasks.ingest import ParseTask

EXTENSIONS = ["fits", "gz", "fz"]  # Filename extensions to strip off


class WhircParseTask(ParseTask):
    """Parser suitable for lab data"""

    def getInfo(self, filename):
        # Grab the basename
        phuInfo, infoList = ParseTask.getInfo(self, filename)
        basename = os.path.basename(filename)
        while any(basename.endswith("." + ext) for ext in EXTENSIONS):
            basename = basename[:basename.rfind('.')]
        phuInfo['basename'] = basename
        return phuInfo, infoList

    def translate_ccd(self, md):
        return 0  # There's only one
