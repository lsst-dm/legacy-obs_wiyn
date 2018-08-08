"""
Whirc-specific overrides for IsrWrapperTask
"""
import os.path

from lsst.utils import getPackageDir
from lsst.obs.wiyn.isr import WhircNullIsrTask
config.isr.retarget(WhircNullIsrTask)

#ObsConfigDir = os.path.join(getPackageDir("obs_wiyn", "config")
#config.isr.load(os.path.join(ObsConfigDir, "isr.py"))
