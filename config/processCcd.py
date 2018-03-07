# Don't do ISR right now
from lsst.obs.wiyn.isr import WhircNullIsrTask
config.isr.retarget(WhircNullIsrTask)
