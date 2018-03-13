from __future__ import print_function

from datetime import (datetime, timedelta)
import os
import re

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

        It might be better to use the 1000*runNo + seqNo,
        but the latter isn't currently set

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
        # relative to 2010-01-01, just to make the visits ints a bit smaller
        mmjd = mjd - 55197
        return int(1e5*mmjd)  # 86400s per day, so we need this resolution


class WhircStackParseTask(ParseTask):
    """Parser suitable for stacked data

    Stacke data are from a sequence of dithered observations
    that have been ISRed and stacked together.
    """

    def getInfo(self, filename):
        # Grab the basename
        phuInfo, infoList = ParseTask.getInfo(self, filename)
        basename = os.path.basename(filename)
        while any(basename.endswith("." + ext) for ext in EXTENSIONS):
            basename = basename[:basename.rfind('.')]
        phuInfo['basename'] = basename
        # Extract 'seq' from filename.  It's not stored in header.
        basenameRegex = "([^_]+)_([A-Z])_(J|H|KS)_([0-9]{8,})"
        field, seq, filt, night = re.match(basenameRegex, basename).groups()
        phuInfo['field'] = field
        phuInfo['seq'] = seq
        phuInfo['night'] = int(night)
        return phuInfo, infoList

    def translate_visit(self, md):
        """Generate a unique visit from the timestamp.

        It might be better to use the 1000*runNo + seqNo,
        but the latter isn't currently set

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
        # relative to 2010-01-01, just to make the visits ints a bit smaller
        mmjd = mjd - 55197
        return int(1e5*mmjd)  # 86400s per day, so we need this resolution

    def translate_expnum(self, md):
        """Generate an expnum for a stack

        Take the first individual image used in the image combination

        Parameters
        ----------
        md : `lsst.daf.base.PropertyList or PropertySet`
            image metadata

        Returns
        -------
        expnum : `int`
            Exposure number
        """
        ref_obj = md.get('IMCMB001')
        return self.__extract_expnum_from_imcb(ref_obj)

    def __extract_expnum_from_imcb(self, ref_obj):
        """Extract the expnum of the reference (first) individual image in a stack.

        Notes:
        This is a separate function to make it easy to test without having
        to construct a metadata object.

        Returns
        -------
        expnum : `int`

        >>> self.__extract_expnum_from_imcb('obj__104.wreg.fits')
        104
        >>> self.__extract_expnum_from_imcb('Obj__245.wreg.fits')
        245
        >>> self.__extract_expnum_from_imcb('obj_535.wreg.fits')
        535
        """
        expnum_extract = re.compile(".+_+([0-9]{3})\.wreg.fits")
        expnum = expnum_extract.match(ref_obj).groups()[0]
        return int(expnum)

    def getDestination(self, butler, info, filename):
        """Get destination for the file

        @param butler      Data butler
        @param info        File properties, used as dataId for the butler
        @param filename    Input filename
        @return Destination filename
        """
        dataset = 'stack'
        destination = butler.get("%s_filename" % dataset, info)[0]
        # Ensure filename is devoid of cfitsio directions about HDUs
        c = destination.find("[")
        if c > 0:
            destination = destination[:c]
        return destination
