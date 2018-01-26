from app.media_parser.__base__ import BaseParser, DateRespector

class SkipParser(BaseParser):
    USELESS_DATE_KEYS=[]
    KNOWN_DATE_KEYS = DateRespector.gather_keys(BaseParser.FILE_KEYS, USELESS_DATE_KEYS)

    FILE_SUFFIX = ['.cpi']

    @staticmethod
    def check_extension(lowerExt):
        return lowerExt in SkipParser.FILE_SUFFIX

    def known_date_keys(self):
        return SkipParser.KNOWN_DATE_KEYS

    @staticmethod
    def determine_datetime(dict):
        return None

class UnknownParser(BaseParser):
    KNOWN_DATE_KEYS = DateRespector.gather_keys(BaseParser.FILE_KEYS)

    @staticmethod
    def check_extension(filename):
        return True

    def known_date_keys(self):
        return UnknownParser.KNOWN_DATE_KEYS

    @staticmethod
    def determine_datetime(dict):
        return None
