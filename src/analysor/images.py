from . import BaseAnalysor, DateRespector

class _:
    EXIF_KEYS = DateRespector('EXIF',
                              ['DateTimeOriginal',
                               'CreateDate',
                               'ModifyDate'], by_first=True, by_min=False)
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


class JpgAnalysor(BaseAnalysor):

    USELESS_DATE_KEYS=['ICC_Profile:ProfileDateTime',
                       'IPTC:DigitalCreationDate',
                       'IPTC:DateCreated',
                       'Composite:GPSDateTime',
                       'EXIF:GPSDateStamp',
                       'MakerNotes:DateDisplayFormat']
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.EXIF_KEYS,
        _.XMP_KEYS,
        _.COMPOSITE_KEYS,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def get_extensions(self):
        return ['.jpg', '.jpeg']

    def known_date_keys(self):
        return JpgAnalysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.EXIF_KEYS,
                _.XMP_KEYS,
                _.COMPOSITE_KEYS]

class PngAnalysor(BaseAnalysor):
    USELESS_DATE_KEYS=[]
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.XMP_KEYS,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def get_extensions(self):
        return ['.png']

    def known_date_keys(self):
        return PngAnalysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.XMP_KEYS]

