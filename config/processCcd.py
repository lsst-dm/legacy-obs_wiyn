# Don't do ISR right now
# from lsst.obs.wiyn.whirc.isr import WhircIsrTask
# calib.isr.retarget(WhircIsrTask)

# calib.isr.doBias = False
# calib.isr.doDark = False
# calib.isr.doFlat = False
# calib.isr.doWrite = False
# calib.isr.assembleCcd.setGain = False

# Focus on post-ISR, post-dither-mosaicing images:
calib.calibrate.repair.doCosmicRay = False # Currently troublesome: lots of pixels that need to be masked first
calib.calibrate.repair.cosmicray.nCrPixelMax = 100000
