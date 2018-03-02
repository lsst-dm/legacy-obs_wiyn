from lsst.obs.wiyn.ingest import WhircParseTask

config.parse.retarget(WhircParseTask)

config.parse.translation = {
    'expTime': 'EXPTIME',
    'object': 'OBJECT',
    'imageType': 'IMGTYPE',
    'filter': 'FILTER1',
    'date': 'DATE-OBS',
    'dateObs': 'DATE-OBS',
    'imageType': 'IMGTYPE',
}
config.parse.translators = {
    'visit': 'translate_visit',
}
config.register.columns = {
    'visit': 'int',
    'basename': 'text',
    'filter': 'text',
    'date': 'text',
    'dateObs': 'text',
    'night': 'int',
    'expTime': 'double',
    'expnum': 'int',
    'ccd': 'int',
    'object': 'text',
    'imageType': 'text',
}
config.register.visit = list(config.register.columns.keys())
config.register.unique = ['visit']
