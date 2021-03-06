import abc
import functools
import pyexifinfo as exif
import time

from copy import copy, deepcopy
from datetime import datetime

import yaml

from utils import distinct_list

class DateRespector:
    TIME_FORMAT = ['%Y:%m:%d %H:%M:%S', '%Y:%m:%d %H:%M:%S%z']

    def __init__(self, group, keys, by_first = False, by_min = True):
        self.group = group
        self.keys = keys
        self.__full_keys__ = DateRespector.__expand_keys__(group=group, short_keys=keys)
        self.by_first = by_first
        self.by_min = by_min
        assert by_first != by_min

    @staticmethod
    def __expand_keys__(group, short_keys):
        return list('{0}:{1}'.format(group, k) for k in short_keys)

    def full_keys(self):
        return self.__full_keys__

    def determine_date(self, dict):
        values_ = list(dict.get(k) for k in self.full_keys())
        values = list(x for x in values_ if x != None)
        values = distinct_list(values)
        dates = list(map(lambda v : DateRespector.__str_to_datetime__(v), values))
        dates = list(x for x in dates if x != None)
        if len(dates) > 0:
            if self.by_first:
                return dates[0]
            elif self.by_min:
                return min(dates, key=lambda x : time.mktime(x.timetuple()))
        return None

    @staticmethod
    def flatten_keys(res):
        if isinstance(res, DateRespector):
            return res.__full_keys__
        elif isinstance(res, list):
            return res
        else:
            return []

    @staticmethod
    def gather_keys(*respectors):
        return functools.reduce((lambda a,b: a + b), list(DateRespector.flatten_keys(r) for r in respectors))

    @staticmethod
    def __str_to_datetime__(str):
        pp = str.find('+')
        if(pp > 0):
            rest = str[pp:].replace(':', '')
            str = str[0:pp] + rest

        for f in DateRespector.TIME_FORMAT:
            try:
                return datetime.strptime(str, f);
            except:
                continue
        return None

class DateRespectors:
    XMP_KEYS = DateRespector('XMP',
                             ['CreateDate',
                              'ModifyDate',
                              'MetadataDate',
                              'PantryMetadataDate',
                              'DateCreated',
                              'DateTimeOriginal',
                              'DateTimeDigitized'])
class MediaFactor:
    def __init__(self, src, shot_datetime = None, exif_data = None):
        self.__exif_data__ = exif_data
        self.src = src
        self.file_size = exif_data.get('File:FileSize')

        self.dates = dict((k, v) for (k, v) in exif_data.items() if 'Date' in k)
        self.date_list = sorted(x[0].split(':') + [x[1], x[0]] for x in self.dates.items())
        self.date_groups = MediaFactor.__group_by__(self.date_list, 0)

        self.mtime = DateRespector.__str_to_datetime__(exif_data.get('File:FileModifyDate'))
        self.datetime = shot_datetime
        self.warning = {}

    def set_datetime(self, datetime):
        self.datetime = datetime
    def set_warning(self, key, value):
        self.warning[key] = value

    def __str2__(self):
        group_strings = []
        file_group_str = None
        for (g, gs) in self.date_groups.items():
            group_string = self.__group_str__(g, gs)
            if g == 'File':
                file_group_str = group_string
                continue
            group_strings.append(group_string)
        if file_group_str != None:
            group_strings.append(file_group_str)
        full_time_string = ', '.join(group_strings)
        result = '{0}({1})[{2}], {3}'.format(self.src, self.file_size, self.datetime, full_time_string)
        return result

    def __str__(self):
        grouped_dates = {}
        for (g, gs) in self.date_groups.items():
            one_grp_by_date = self.__group_in_dict_by_date__(gs)
            grouped_dates[g] = one_grp_by_date
        grouped_dates['Final'] = self.datetime
        res_obj = {
            'File': '{0}({1})'.format(self.src, self.file_size)
        }
        res_obj['Time'] = grouped_dates
        return yaml.dump(res_obj, default_flow_style=False, allow_unicode=True)

    def __group_in_dict_by_date__(self, gs):
        res = {}
        group_by_v = MediaFactor.__group_by__(gs, 2)
        for (dt, samples) in group_by_v.items():
            res[dt] = list(s[3] for s in samples)
        return res

    def __group_str__(self, g, gs):
        group_by_v = MediaFactor.__group_by__(gs, 2)
        value_strings = []
        for (v, samples) in group_by_v.items():
            same_value_keys = list(x[1] for x in samples)
            key_string = '(' + ','.join(same_value_keys) + '-> {0})'.format(v)
            value_strings.append(key_string)
        group_string = '{0}[{1}]'.format(g, ', '.join(value_strings))
        return group_string

    @staticmethod
    def __group_by__(sample_list, key_col):
        grouped = {}
        for s in sample_list:
            MediaFactor.__group_one_sample__(grouped, s, key_col)
        return grouped

    @staticmethod
    def __group_one_sample__(grouped, sample, key_col):
        grp = sample[key_col]
        siblings = grouped.get(grp)
        if siblings == None:
            siblings = []
            grouped[grp] = siblings
        siblings.append(sample)

class BaseAnalysor:
    FILE_KEYS = DateRespector('File',
                              ['FileAccessDate',
                               'FileInodeChangeDate',
                               'FileModifyDate'], by_first=False, by_min=True)

    def __init__(self, respect_mtime):
        self.respect_mtime=respect_mtime

    def known_date_keys(self):
        return DateRespector.gather_keys(BaseAnalysor.FILE_KEYS)

    def date_respectors(self):
        return []

    def calc_factor(self, filename):
        exif_data = self._get_exif_(filename)
        factor = MediaFactor(src=filename, exif_data=exif_data)

        unknown_data = dict((x[3],x[2]) for x in factor.date_list if x[3] not in self.known_date_keys())
        if len(unknown_data):
            factor.set_warning('unknown exif', unknown_data)

        shotDt = self.determine_datetime(factor)
        if shotDt != None:
            factor.set_datetime(shotDt)
        self.pre_return_factor(factor=factor)
        return factor
    def pre_return_factor(self, factor):
        pass

    _KEY_MAPPING_ = {
        "ExifIFD": 'EXIF',
        "IFD0": 'EXIF',
        "IFD1": 'EXIF',
        "InteropIFD": 'EXIF',
        "System": 'File'
    }

    @staticmethod
    def _key_mapping_(make):
        km = deepcopy(BaseAnalysor._KEY_MAPPING_)
        maker_key = None
        if make in ['OLYMPUS CORPORATION', 'OLYMPUS IMAGING CORP.']:
            maker_key = 'Olympus'
        else:
            raise RuntimeError('Unknown maker: {0}'.format(make))

        if maker_key:
            km[maker_key] = 'MakerNotes'
        return km

    @staticmethod
    def _translate_key_v_(dict, key_map, key):
        val = dict.get(key)
        (kg, k) = key.split(':', 1)
        kgm = key_map.get(kg)
        if kgm:
            key = key.replace(kg, kgm, 1)
        return (key, val)

    def _get_exif_(self, filename):
        try:
            orig_exif = exif.information(filename)
            return orig_exif
        except Exception as e:
            pass

        import xmltodict
        raw_xml_obj = xmltodict.parse(exif.get_xml(filename))
        xml_obj = raw_xml_obj['rdf:RDF']['rdf:Description']
        maker_des = xml_obj['IFD0:ImageDescription']
        make = xml_obj['IFD0:Make']
        key_mapping = BaseAnalysor._key_mapping_(make)
        trans_xml_obj = dict(BaseAnalysor._translate_key_v_(xml_obj,key_mapping,k) for k in xml_obj.keys() if not k.startswith('@'))

        return trans_xml_obj

    def determine_datetime(self, factor):
        dict = factor.dates
        for resp in self.date_respectors():
            dt = resp.determine_date(dict)
            if dt != None:
                return dt
        if self.respect_mtime:
            return factor.mtime
        return None

    @abc.abstractmethod
    def get_extensions(self):
        return None

    def check_extension(self, ext):
        exts = self.get_extensions()
        return ext.lower() in exts

class GenericAnalysor(BaseAnalysor):
    def date_respectors(self):
        return [BaseAnalysor.FILE_KEYS]

    def __init__(self, respect_mtime):
        super().__init__(respect_mtime=respect_mtime)
