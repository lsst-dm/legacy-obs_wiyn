from lsst.obs.wiyn.whirc.isr import WhircIsrTask
root.isr.retarget(WhircIsrTask)

root.isr.doBias = False
root.isr.doDark = True
root.isr.doFlat = True
root.isr.doWrite = False

root.calibrate.repair.doCosmicRay = False # Currently troublesome: lots of pixels that need to be masked first
root.calibrate.repair.cosmicray.nCrPixelMax = 100000
