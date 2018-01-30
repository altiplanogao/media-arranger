import os

from .images import *
from .videos import *
from .others import SkipAnalysor, UnknownAnalysor

__all__ = {
    'get_analysor'
}

def __gen_ext_to_parser__():
    ext_to_parser = {}
    parsers = [
        JpgAnalysor(),
        PngAnalysor(),
        MovAnalysor(),
        Mp4Analysor(),
        MtsAnalysor(),
        V3gpAnalysor(),
        SkipAnalysor(),
        UnknownAnalysor()
    ]
    for p in parsers:
        for ext in p.get_extensions():
            ext_to_parser[ext] = p
    return ext_to_parser

__ext_to_parser__ = __gen_ext_to_parser__()

def get_analysor(filename):
    fn, file_extension = os.path.splitext(filename)
    lowerExt = file_extension.lower()
    p = __ext_to_parser__.get(lowerExt)
    return p
