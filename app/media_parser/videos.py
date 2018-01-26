from app.media_parser.__base__ import DateRespector, BaseParser

class _:
    QT_MEDIA_DATE_KEYS = DateRespector('QuickTime',
                                       ['MediaCreateDate',
                                        'MediaModifyDate'])
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
                                      'ContentCreateDate-chi',
                                      'CreationDate-chi-HK'])
    H264_MEDIA_DATE_KEYS = DateRespector('H264', ['DateTimeOriginal'])

class Mp4Parser(BaseParser):
    USELESS_DATE_KEYS=['QuickTime:CreationDate']
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.QT_MEDIA_DATE_KEYS,
        _.QT_TRACK_DATE_KEYS,
        _.QT_MC_DATE_KEYS,
        BaseParser.FILE_KEYS,
        USELESS_DATE_KEYS)

    FILE_SUFFIX = ['.mp4']

    @staticmethod
    def check_extension(lowerExt):
        return lowerExt in Mp4Parser.FILE_SUFFIX

    def known_date_keys(self):
        return Mp4Parser.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.QT_MEDIA_DATE_KEYS,
                _.QT_TRACK_DATE_KEYS,
                _.QT_MC_DATE_KEYS]


class MovParser(BaseParser):
    USELESS_DATE_KEYS=[]
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.QT_MEDIA_DATE_KEYS,
        _.QT_TRACK_DATE_KEYS,
        _.QT_MC_DATE_KEYS,
        _.QT_CONT_DATE_KEY,
        BaseParser.FILE_KEYS,
        USELESS_DATE_KEYS)

    FILE_SUFFIX = ['.mov']

    @staticmethod
    def check_extension(lowerExt):
        return lowerExt in MovParser.FILE_SUFFIX

    def known_date_keys(self):
        return MovParser.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [
            _.QT_MC_DATE_KEYS,
            _.QT_MEDIA_DATE_KEYS,
            _.QT_TRACK_DATE_KEYS,
            _.QT_CONT_DATE_KEY]
        return None

class MtsParser(BaseParser):
    USELESS_DATE_KEYS=['']
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.H264_MEDIA_DATE_KEYS,
        BaseParser.FILE_KEYS,
        USELESS_DATE_KEYS)

    FILE_SUFFIX = ['.mts']

    @staticmethod
    def check_extension(lowerExt):
        return lowerExt in MtsParser.FILE_SUFFIX

    def known_date_keys(self):
        return MtsParser.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.H264_MEDIA_DATE_KEYS]
        return None
