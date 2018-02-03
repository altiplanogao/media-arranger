from . import BaseAnalysor, DateRespector


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
                                    'SubSecModifyDate'])

class Mp3Analysor(BaseAnalysor):
    USELESS_DATE_KEYS=[]
    KNOWN_DATE_KEYS = DateRespector.gather_keys(
        _.COMPOSITE_KEYS,
        BaseAnalysor.FILE_KEYS,
        USELESS_DATE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.mp3']

    def known_date_keys(self):
        return Mp3Analysor.KNOWN_DATE_KEYS

    def date_respectors(self):
        return [_.COMPOSITE_KEYS]

    def pre_return_factor(self, factor):
        super().pre_return_factor(factor)


