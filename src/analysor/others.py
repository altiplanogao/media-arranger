from . import BaseAnalysor, DateRespector

class SkipAnalysor(BaseAnalysor):
    USELESS_DATE_KEYS=[]

    def get_extensions(self):
        return ['.cpi']

class UnknownAnalysor(BaseAnalysor):
    KNOWN_DATE_KEYS = DateRespector.gather_keys(BaseAnalysor.FILE_KEYS)

    def get_extensions(self):
        return []
