from . import BaseAnalysor, DateRespector, DateRespectors


class _:
    EXIF_KEYS = DateRespector('EXIF',
                              ['DateTimeOriginal',
                               'CreateDate',
                               'ModifyDate'], by_first=True, by_min=False)

    COMPOSITE_KEYS = DateRespector('Composite',
                                   ['SubSecCreateDate',
                                    'DateTimeCreated',
                                    'DateTimeOriginal',
                                    'DigitalCreationDateTime',
                                    'SubSecDateTimeOriginal',
                                    'SubSecModifyDate',
                                    'SubSecCreateDate'])
    MARK_KEYS = DateRespector('MakerNotes',['SonyDateTime'])


class JpgAnalysor(BaseAnalysor):

    USELESS_DATE_KEYS=['ICC_Profile:ProfileDateTime',
                       'IPTC:DigitalCreationDate',
                       'IPTC:DateCreated',
                       'Composite:GPSDateTime',
                       'Composite:DateCreated',
                       'EXIF:GPSDateStamp',
                       'FlashPix:ExtensionCreateDate',
                       'FlashPix:ExtensionModifyDate',
                       'MakerNotes:Date',
                       'MakerNotes:DateStampMode',
                       'MakerNotes:DateDisplayFormat',
                       'MakerNotes:DateTimeStamp']
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.EXIF_KEYS,
        DateRespectors.XMP_KEYS,
        _.COMPOSITE_KEYS,
        _.MARK_KEYS,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.jpg', '.jpeg', '.nef', '.heic']

    def known_date_keys(self):
        return JpgAnalysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.EXIF_KEYS,
                DateRespectors.XMP_KEYS,
                _.COMPOSITE_KEYS]
    def pre_return_factor(self, factor):
        super().pre_return_factor(factor)

class PngAnalysor(BaseAnalysor):
    USELESS_DATE_KEYS=[]
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        DateRespectors.XMP_KEYS,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.png']

    def known_date_keys(self):
        return PngAnalysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [DateRespectors.XMP_KEYS]

class GifAnalysor(BaseAnalysor):
    USELESS_DATE_KEYS=[]
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        DateRespectors.XMP_KEYS,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.gif']

    def known_date_keys(self):
        return GifAnalysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [DateRespectors.XMP_KEYS]

    def pre_return_factor(self, factor):
        super().pre_return_factor(factor)
