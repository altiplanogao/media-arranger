import os

from .images import *
from .videos import *
from .others import SkipParser, UnknownParser

def media_parser(filename):
    fn, file_extension = os.path.splitext(filename)
    lowerExt = file_extension.lower()
    if JpgParser.check_extension(lowerExt):
        return JpgParser()
    elif PngParser.check_extension(lowerExt):
        return PngParser()
    elif MovParser.check_extension(lowerExt):
        return MovParser()
    elif Mp4Parser.check_extension(lowerExt):
        return Mp4Parser()
    elif MtsParser.check_extension(lowerExt):
        return MtsParser()
    elif SkipParser.check_extension(lowerExt):
        return SkipParser()
    elif UnknownParser.check_extension(lowerExt):
        return UnknownParser()
    return None