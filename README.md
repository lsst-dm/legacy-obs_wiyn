LSST DM Pipeline for WIYN+WHIRC Data.

Example usage:
DESIRED

mkdir WIYN
echo 'lsst.obs.wiyn.WhircMapper' > WIYN/_mapper
ingestImages.py WIYN ${HOME}/release/DR2_images_alpha/\*.fits --mode link

processCcd.py ...  Generate photometry catalogs.
LOAD CATALOGS INTO DATABASE?

Future goals:
forcedPhotometry
diffIm
forcedPhotometry on subtractions

Currently focused on processing images after instrument signature removal.

Thus the WhircMapper.paf file is half just the bookeeping for the filename structure MWV used for the SweetSpot survey.
