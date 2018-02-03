from . import DateRespector, BaseAnalysor, DateRespectors


class _:
    QT_MEDIA_DATE_KEYS = DateRespector('QuickTime',
                                       ['MediaCreateDate',
                                        'MediaModifyDate',
                                        'ContentCreateDate'])
    QT_TRACK_DATE_KEYS = DateRespector('QuickTime',
                                       ['TrackCreateDate',
                                        'TrackModifyDate'])
    QT_MC_DATE_KEYS = DateRespector('QuickTime',
                                    ['CreationDate',
                                     'CreateDate',
                                     'ModifyDate'])
    QT_CONT_DATE_KEY = DateRespector('QuickTime',
                                     ['ContentCreateDate',
                                      'ContentCreateDate-zho',
                                      'CreationDate-zho-CN',
                                      'CreationDate-zho-HK',
                                      'CreationDate-und-US',
                                      'ContentCreateDate-chi',
                                      'CreationDate-chi-HK'])
    H264_MEDIA_DATE_KEYS = DateRespector('H264',
                                         ['DateTimeOriginal'])

class MpgAnalysor(BaseAnalysor):
    USELESS_DATE_KEYS=[]
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.mpg']

    def known_date_keys(self):
        return MpgAnalysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return []

    def pre_return_factor(self, factor):
        super().pre_return_factor(factor)

class Mp4Analysor(BaseAnalysor):
    USELESS_DATE_KEYS=['QuickTime:CreationDate']
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        DateRespectors.XMP_KEYS,
        _.QT_MEDIA_DATE_KEYS,
        _.QT_TRACK_DATE_KEYS,
        _.QT_MC_DATE_KEYS,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.mp4', '.m4a']

    def known_date_keys(self):
        return Mp4Analysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [DateRespectors.XMP_KEYS,
                _.QT_MEDIA_DATE_KEYS,
                _.QT_TRACK_DATE_KEYS,
                _.QT_MC_DATE_KEYS]

class MovAnalysor(BaseAnalysor):
    USELESS_DATE_KEYS=['QuickTime:PreviewDate']
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.QT_MEDIA_DATE_KEYS,
        _.QT_TRACK_DATE_KEYS,
        _.QT_MC_DATE_KEYS,
        _.QT_CONT_DATE_KEY,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.mov', '.3gp']

    def known_date_keys(self):
        return MovAnalysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [
            _.QT_MC_DATE_KEYS,
            _.QT_MEDIA_DATE_KEYS,
            _.QT_TRACK_DATE_KEYS,
            _.QT_CONT_DATE_KEY]

class MtsAnalysor(BaseAnalysor):
    USELESS_DATE_KEYS=['']
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.H264_MEDIA_DATE_KEYS,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.mts']

    def known_date_keys(self):
        return MtsAnalysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.H264_MEDIA_DATE_KEYS]
