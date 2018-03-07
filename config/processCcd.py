# Don't do ISR right now
from lsst.obs.wiyn.isr import WhircIsrTask
config.isr.retarget(WhircIsrTask)

config.isr.doBias = False
config.isr.doDark = False
config.isr.doFlat = False
config.isr.doWrite = False
