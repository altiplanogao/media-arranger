import os

from analysor import GenericAnalysor
from .images import *
from .videos import *
from .audios import *
from .others import SkipAnalysor, UnknownAnalysor

__all__ = {
    'analysors'
}

class analysors:
    def __init__(self, respect_mtime):
        self.respect_mtime = respect_mtime
        ext_to_parser = {}
        parsers = [
            JpgAnalysor(respect_mtime),
            PngAnalysor(respect_mtime),
            GifAnalysor(respect_mtime),

            MpgAnalysor(respect_mtime),
            MovAnalysor(respect_mtime),
            Mp4Analysor(respect_mtime),
            MtsAnalysor(respect_mtime),

            Mp3Analysor(respect_mtime),

            SkipAnalysor(respect_mtime),
            UnknownAnalysor(respect_mtime)
        ]
        for p in parsers:
            for ext in p.get_extensions():
                ext_to_parser[ext] = p
        self.ext_to_parser = ext_to_parser
        self.generic = GenericAnalysor(respect_mtime)

    def get_analysor(self, filename):
        fn, file_extension = os.path.splitext(filename)
        lowerExt = file_extension.lower()
        p = self.ext_to_parser.get(lowerExt)
        return p

    def get_generic(self):
        return self.generic
