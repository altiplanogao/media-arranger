from . import BaseAnalysor, DateRespector

class SkipAnalysor(BaseAnalysor):
    USELESS_DATE_KEYS=[]

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return ['.cpi','.doc','.thm']

class UnknownAnalysor(BaseAnalysor):
    KNOWN_DATE_KEYS = DateRespector.gather_keys(BaseAnalysor.FILE_KEYS)

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)

    def get_extensions(self):
        return []
