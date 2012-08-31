#!/usr/bin/env python

# Date Created: 2012/08/31 - MWV
# Based off of the obs_sst/bin/getInputRegistry.py put together by Paul Price.
# Purpose:
# Loads in images from WIYN WHIRC SN NIR survey.

import glob
import os
import re
import sqlite3 as sqlite
import sys
import datetime
import lsst.daf.base   as dafBase
import lsst.pex.policy as pexPolicy
import lsst.afw.image  as afwImage


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--create", default=False, action="store_true", help="Create new registry (clobber old)?")
parser.add_argument("--root", default=".", help="Root directory")
args = parser.parse_args()

root = args.root
if root == '-':
    files = [l.strip() for l in sys.stdin.readlines()]
else:
    files = glob.glob(os.path.join(root, "*", "????????", "*.fits"))
sys.stderr.write('processing %d files...\n' % (len(files)))

registryName = "registry.sqlite3"
if os.path.exists(registryName) and args.create:
    os.unlink(registryName)

makeTables = not os.path.exists(registryName)
conn = sqlite.connect(registryName)
if makeTables:
    cmd = "create table raw (id integer primary key autoincrement"
    cmd += ", field text, year int, month int, day int, mjd float"
    cmd += ", expnum int, filter text, filter1 text, filter2 text"
    cmd += ", observer text, ra text, dec text, airmass float, focus float"
    cmd += ", filename text, recid text"
    cmd += ", date text, datetime text, unique(year, month, day, expnum))"
    conn.execute(cmd)
    conn.commit()

for fits in files:
    matches = re.search(r"(\S+)/(\d{4})(\d{2})(\d{2})/(dark|flat|obj)_([JHK]_|)(\d{3})\.fits", fits) 
    if not matches:
        print >>sys.stderr, "Warning: skipping unrecognized filename:", fits
        continue

    sys.stderr.write("Processing %s\n" % (fits))

    # "filterdummy" is set for flats, but not for science exposures.
    # So we rely on the FITS header for filter information
    basedir, year, month, day, imagetype, filterdummy, expnum = matches.groups()
    date = year+month+day

    field = None
    year  = int(year)
    month = int(month)
    day   = int(day)
    expnum = int(expnum)
    
    # Extract filter information from header
    im = afwImage.ExposureF(fits)
    h = im.getMetadata()
    mjd = h.get('MJD-OBS')
    filt1 = h.get('FILTER1').strip() 
    filt2 = h.get('FILTER2').strip() 
    filt = filt1  # We're using the FILTER1 wheel.  Ignore 'FILTER2' which should always say 'OPEN'
    observer = h.get('OBSERVER').strip()
    ra = h.get('RA').strip()
    dec= h.get('DEC').strip() 
    airmass = h.get('AIRMASS')
    focus = h.get('FOCUS')
    recid = h.get('RECID').strip()

    dateobsstr = h.get('DATE-OBS')
    
    dateObs = (datetime.datetime(year, month, day)).isoformat()

    try:
        conn.execute("INSERT INTO raw VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     (field, year, month, day, mjd,
                      expnum, filt, filt1, filt2, 
                      observer, ra, dec, airmass, focus,
                      fits, recid,
                      date, dateObs))

    except Exception, e:
        print "skipping botched %s: %s" % (fits, e)
        continue

conn.commit()
conn.close()
