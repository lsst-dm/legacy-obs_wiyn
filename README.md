LSST DM Pipeline for WIYN+WHIRC Data.

Example usage:
DESIRED

```
mkdir WIYN
echo 'lsst.obs.wiyn.WhircMapper' > WIYN/_mapper

# For ingesting raws:
## We ingest all raws: dark, flat, and on-sky
ingestImages.py WIYN ${TESTDATA_WHIRC_DIR}/raw/20111115/*.fits --mode link

# For ingesting the stacks
# This --create will only work the first time, when we still need to create 'stack' and 'stack_visit'
# Once they exist, running again with --create would lead to an error
ingestImages.py WIYN /Users/wmwv/Research/SweetSpot/DR1_data/stacks/s_alpha/\*.fits --mode link --configfile ${OBS_WIYN_DIR}/config/ingestStack.py --create
```

processCcd.py WIYN --id basename=iPTF13ebh_A_J_20131120 --output WIYN --configfile ${OBS_WIYN_DIR}/config/processCcd.py

processCcd.py WIYN --id basename=iPTF13ebh_A_J_20131120 --output WIYN --clobber-config --clobber-versions

Generate photometry catalogs.
LOAD CATALOGS INTO DATABASE?

Future goals:
forcedPhotometry
diffIm
forcedPhotometry on subtractions

Currently focused on processing images after instrument signature removal.

Thus the WhircMapper.paf file is half just the bookeeping for the filename structure MWV used for the SweetSpot survey.
