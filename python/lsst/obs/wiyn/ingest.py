from __future__ import print_function

from datetime import (datetime, timedelta)
import os

from lsst.pipe.tasks.ingest import ParseTask

EXTENSIONS = ["fits", "gz", "fz"]  # Filename extensions to strip off


class WhircParseTask(ParseTask):
    """Parser suitable for raw data"""

    def getInfo(self, filename):
        # Grab the basename
        phuInfo, infoList = ParseTask.getInfo(self, filename)
        basename = os.path.basename(filename)
        while any(basename.endswith("." + ext) for ext in EXTENSIONS):
            basename = basename[:basename.rfind('.')]
        phuInfo['basename'] = basename
        expnum = int(basename.split('_')[-1])
        phuInfo['expnum'] = expnum
        # This is a little hokey
        # The UTC is *almost* always a day ahead of the
        # beginning of the evening at KPNO (MST=UTC-7).
        # Exception is during the winter
        # when we start observations before 17:00 MST.
        # Should do this using an actual datetime object and add one hour
        # Then take the YYYYMMDD of the UTC time.
        dateobs = phuInfo['date'][:-2]  # strip off the decimal seconds
        dt = datetime.strptime(dateobs+' UTC', '%Y-%m-%dT%H:%M:%S %Z')
        dt = dt - timedelta(hours=23)
        night = int(dt.strftime("%Y%m%d"))
        phuInfo['night'] = night
        return phuInfo, infoList

    def translate_ccd(self, md):
        return 0  # There's only one

    def translate_visit(self, md):
        """Generate a unique visit from the timestamp.

        It might be better to use the 1000*runNo + seqNo, but the latter isn't currently set

        Parameters
        ----------
        md : `lsst.daf.base.PropertyList or PropertySet`
            image metadata

        Returns
        -------
        visit_num : `int`
            Visit number, as translated
        """
        mjd = md.get("MJD-OBS")
        mmjd = mjd - 55197              # relative to 2010-01-01, just to make the visits a tiny bit smaller
        return int(1e5*mmjd)            # 86400s per day, so we need this resolution
