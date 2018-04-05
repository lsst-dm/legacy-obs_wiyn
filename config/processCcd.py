# Don't do ISR right now
from lsst.obs.wiyn.isr import WhircNullIsrTask
config.isr.retarget(WhircNullIsrTask)
from lsst.meas.astrom.matchPessimisticB import MatchPessimisticBTask
config.calibrate.astrometry.matcher.retarget(MatchPessimisticBTask)
