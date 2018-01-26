from .__base__ import BaseParser, DateRespector

class _:
    EXIF_KEYS = DateRespector('EXIF',
                              ['CreateDate',
                               'DateTimeOriginal',
                               'ModifyDate'])
    XMP_KEYS = DateRespector('XMP',
                             ['CreateDate',
                              'ModifyDate',
                              'MetadataDate',
                              'DateCreated'])
    COMPOSITE_KEYS = DateRespector('Composite',
                                   ['SubSecCreateDate',
                                    'DateTimeCreated',
                                    'DigitalCreationDateTime',
                                    'SubSecDateTimeOriginal',
                                    'SubSecModifyDate'])


class JpgParser(BaseParser):

    USELESS_DATE_KEYS=['ICC_Profile:ProfileDateTime',
                       'IPTC:DigitalCreationDate',"IPTC:DateCreated",
                    'Composite:GPSDateTime',
                    'EXIF:GPSDateStamp']
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.EXIF_KEYS,
        _.XMP_KEYS,
        _.COMPOSITE_KEYS,
        BaseParser.FILE_KEYS,
        USELESS_DATE_KEYS)

    FILE_SUFFIX = ['.jpg', '.jpeg']

    @staticmethod
    def check_extension(lowerExt):
        return lowerExt in JpgParser.FILE_SUFFIX

    def known_date_keys(self):
        return JpgParser.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.EXIF_KEYS,
                _.XMP_KEYS,
                _.COMPOSITE_KEYS]


class PngParser(BaseParser):
    USELESS_DATE_KEYS=[]
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.XMP_KEYS,
        BaseParser.FILE_KEYS,
        USELESS_DATE_KEYS)

    FILE_SUFFIX = ['.png']

    @staticmethod
    def check_extension(lowerExt):
        return lowerExt in PngParser.FILE_SUFFIX

    def known_date_keys(self):
        return PngParser.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.XMP_KEYS]

