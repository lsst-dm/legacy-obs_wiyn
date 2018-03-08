from lsst.obs.wiyn.ingest import WhircStackParseTask

config.parse.retarget(WhircStackParseTask)

config.parse.translation = {
    'expTime': 'EXPTIME',
    'imageType': 'IMGTYPE',
    'filter': 'FILTER1',
    'date': 'DATE-OBS',
    'dateObs': 'DATE-OBS',
    'imageType': 'IMGTYPE',
}
config.parse.translators = {
    'visit': 'translate_visit',
    'expnum': 'translate_expnum',
}
config.register.table = 'stack'
config.register.columns = {
    'visit': 'int',
    'basename': 'text',
    'field': 'text',
    'seq': 'text',
    'filter': 'text',
    'night': 'int',
    'date': 'text',
    'dateObs': 'text',
    'expTime': 'double',
    'imageType': 'text',
    'expnum': 'int',
}
config.register.visit = list(config.register.columns.keys())
config.register.unique = ['field', 'seq', 'filter', 'night']
