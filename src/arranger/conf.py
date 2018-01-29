import argparse
import os
import yaml

from arranger import ArrangeMode, DuplicateAction
from datetime import datetime
from logging import config as logging_config
from os import path

class ArgKeys:
    SOURCE_KEY = 'source'
    DESTINATION_KEY = 'destination'
    DOUBTS_DIR_KEY = 'doubts'

    LOG_DIR_KEY = 'log_dir'
    LOG_DIR_DEFAULT_VAL = 'logs'

    ARRANGE_MODE_KEY = 'arrange_mode'
    ARRANGE_MODE_DEFAULT_VAL = ArrangeMode.COPY
    DUPLICATE_ACTION_KEY = 'duplicate_action'
    DUPLICATE_ACTION_DEFAULT_VAL = DuplicateAction.SKIP
    DUPLICATE_DEST_DIR_KEY = 'duplicate_dest_dir'

    RESPECT_MTIME_KEY = 'respect_mtime'
    RESPECT_MTIME_DEFAULT_VAL = 'no'
    ACL_KEY = 'acl'
    ACL_DEFAULT_VAL = 'no'
    ACL_UID_KEY = 'acl_uid'
    ACL_UID_DEFAULT_VAL = 1
    ACL_GID_KEY = 'acl_gid'
    ACL_GID_DEFAULT_VAL = 1
    ACL_FILE_MOD_KEY = 'acl_filemod'
    ACL_FILE_MOD_DEFAULT_VAL = 0x0440
    ACL_DIR_MOD_KEY = 'acl_dirmod'
    ACL_DIR_MOD_DEFAULT_VAL = 0x0551

    TRUES = ['yes', 'true', 'on']
    FALSES = ['no', 'false', 'off']

    @staticmethod
    def get_boolean(v):
        if isinstance(v, (bool)):
            return v
        elif isinstance(v, (str)):
            v = v.lower()
            if (v in ArgKeys.TRUES):
                return True
            elif (v in ArgKeys.FALSES):
                return False
        raise Exception(u"Invalid boolean value '{0}'".format(v))

    @staticmethod
    def get_int(v, base = 10):
        if isinstance(v, int):
            return v
        elif isinstance(v, str):
            return int(v, base=base)

    @staticmethod
    def get_arrange_mode(am):
        if isinstance(am, (ArrangeMode)):
            return am
        elif isinstance(am, (str)):
            try:
                return ArrangeMode[am]
            except:
                return ArrangeMode.NA

    @staticmethod
    def get_duplicate_action(da):
        if isinstance(da, (DuplicateAction)):
            return da
        elif isinstance(da, (str)):
            try:
                return DuplicateAction[da]
            except:
                return DuplicateAction.NA

    @staticmethod
    def hyphen_key(str):
        return str.replace('_', '-');

    @staticmethod
    def underscore_key(str):
        return str.replace('-', '_');

    @staticmethod
    def as_arg_key(str):
        return '--' + str.replace('_', '-');

    @staticmethod
    def get_arg_val(obj, arg_key):
        if isinstance(obj, dict):
            return obj.get(arg_key)
        elif isinstance(obj, argparse.Namespace):
            return getattr(obj, arg_key)
        raise RuntimeError('arg type error')

class AclConf:
    def __init__(self):
        self.chown = False
        self.uid = ArgKeys.ACL_UID_DEFAULT_VAL
        self.gid = ArgKeys.ACL_GID_DEFAULT_VAL
        self.file_mod = ArgKeys.ACL_FILE_MOD_DEFAULT_VAL
        self.dir_mod = ArgKeys.ACL_DIR_MOD_DEFAULT_VAL

class Configure:
    def __init__(self):
        self.src = []
        self.dest = None
        self.doubts = None
        self.log_dir = ArgKeys.LOG_DIR_DEFAULT_VAL
        self.log_file = None

        self.arrange_mode = ArgKeys.ARRANGE_MODE_DEFAULT_VAL
        self.duplicate_action = DuplicateAction.SKIP
        self.duplicate_dest_dir = None

        self.respect_mtime = 'no'
        self.acl = None

    def _set_src(self, src):
        if isinstance(src, str):
            src = [src]
        self.src = src
    def _set_log_dir(self, log_dir):
        self.log_dir = log_dir
        now = datetime.now()
        nowstr = now.strftime('%Y%m%d_%H%M%S')
        self.log_file = path.join(log_dir, nowstr + '.log')
    def _set_arrange_mode(self, am):
        self.arrange_mode = ArgKeys.get_arrange_mode(am)
    def _set_duplicate_action(self, da):
        self.duplicate_action = ArgKeys.get_duplicate_action(da)
    def _set_duplicate_dest_dir(self, ddd):
        self.duplicate_dest_dir = ddd
    def _set_respect_mtime(self, mtime):
        self.respect_mtime = ArgKeys.get_boolean(mtime)
    def _set_acl(self, acl):
        status = ArgKeys.get_boolean(acl)
        if status:
            self.acl = AclConf()
        else:
            self.acl = None
    def _set_acl_uid(self, uid):
        if self.acl:
            self.acl.uid = ArgKeys.get_int(uid)
    def _set_acl_gid(self, gid):
        if self.acl:
            self.acl.gid = ArgKeys.get_int(gid)
    def _set_acl_file_mod(self, file_mod):
        if self.acl:
            self.acl.file_mod = ArgKeys.get_int(file_mod, 8)
    def _set_acl_dir_mod(self, dir_mod):
        if self.acl:
            self.acl.dir_mod = ArgKeys.get_int(dir_mod, 8)

    def set_by_config(self, config_file):
        if config_file == None:
            return False
        if path.isdir(config_file):
            expected_config_file = path.join(config_file, "settings.yml")
            if path.isfile(expected_config_file):
                config_file = expected_config_file
        if path.isfile(config_file):
            with open(config_file, 'r') as stream:
                try:
                    conf = yaml.load(stream)
                    self.set_by_obj(conf)
                except yaml.YAMLError as exc:
                    return False
            return True
        return False

    def set_by_obj(self, obj):
        src = ArgKeys.get_arg_val(obj, ArgKeys.SOURCE_KEY)
        if src:
            self._set_src(src)
        dest = ArgKeys.get_arg_val(obj, ArgKeys.DESTINATION_KEY)
        if dest:
            self.dest = dest
        doubts = ArgKeys.get_arg_val(obj, ArgKeys.DOUBTS_DIR_KEY)
        if doubts:
            self.doubts = doubts
        log_dir = ArgKeys.get_arg_val(obj, ArgKeys.LOG_DIR_KEY)
        if log_dir:
            self._set_log_dir(log_dir)

        arrange_m = ArgKeys.get_arg_val(obj, ArgKeys.ARRANGE_MODE_KEY)
        if arrange_m:
            self._set_arrange_mode(arrange_m)
        da = ArgKeys.get_arg_val(obj, ArgKeys.DUPLICATE_ACTION_KEY)
        if da:
            self._set_duplicate_action(da)
        ddd = ArgKeys.get_arg_val(obj, ArgKeys.DUPLICATE_DEST_DIR_KEY)
        if ddd:
            self._set_duplicate_dest_dir(ddd)

        rmtime = ArgKeys.get_arg_val(obj, ArgKeys.RESPECT_MTIME_KEY)
        if rmtime != None:
            self._set_respect_mtime(rmtime)

        acl = ArgKeys.get_arg_val(obj, ArgKeys.ACL_KEY)
        if acl != None:
            self._set_acl(acl)
        acl_uid = ArgKeys.get_arg_val(obj, ArgKeys.ACL_UID_KEY)
        if acl_uid:
            self._set_acl_uid(acl_uid)
        acl_gid = ArgKeys.get_arg_val(obj, ArgKeys.ACL_GID_KEY)
        if acl_gid:
            self._set_acl_gid(acl_gid)
        acl_fm = ArgKeys.get_arg_val(obj, ArgKeys.ACL_FILE_MOD_KEY)
        if acl_fm:
            self._set_acl_file_mod(acl_fm)
        acl_dm = ArgKeys.get_arg_val(obj, ArgKeys.ACL_DIR_MOD_KEY)
        if acl_dm:
            self._set_acl_dir_mod(acl_dm)

    def complete(self):
        if self.arrange_mode == ArrangeMode.COPY:
            self.duplicate_action = DuplicateAction.SKIP

        if not path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        logging_conf_file = path.join(path.dirname(__file__),'logging.yml')
        if path.isfile(logging_conf_file):
            with open(logging_conf_file, 'r') as stream:
                try:
                    conf = yaml.load(stream)
                    conf.get('handlers').get('file')['filename'] = self.log_file
                    logging_config.dictConfig(conf)
                except yaml.YAMLError as exc:
                    print(exc)

    def to_dict(self):
        result = self.__dict__.copy()
        result['work directory'] = os.getcwd()
        return result

def __make_parser__():
    parser = argparse.ArgumentParser(description='Arrange media files.')
    parser.add_argument('-s', ArgKeys.as_arg_key(ArgKeys.SOURCE_KEY),
                        nargs='+',
                        help='set source directories')
    parser.add_argument('-d', ArgKeys.as_arg_key(ArgKeys.DESTINATION_KEY),
                        help='set destination directory')
    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.DOUBTS_DIR_KEY),
                        help='set doubts directory')
    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.LOG_DIR_KEY),
                        help='log directory')

    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.ARRANGE_MODE_KEY),
                        choices=['COPY', 'MOVE'],
                        help='arrange by move or copy')
    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.DUPLICATE_ACTION_KEY),
                        choices=['DROP', 'SKIP', 'MOVE'],
                        help='whether drop the source file on duplicated. Only works on "{}" == "MOVE"'.format(ArgKeys.ARRANGE_MODE_KEY))
    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.DUPLICATE_DEST_DIR_KEY),
                        help='move the duplicated source files here. Only works on "{0}" == "MOVE" and "{1}" == "MOVE"'.format(ArgKeys.ARRANGE_MODE_KEY, ArgKeys.DUPLICATE_ACTION_KEY))

    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.RESPECT_MTIME_KEY),
                        choices=['yes', 'no'],
                        help='whether use mtime on missing exif time')

    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.ACL_KEY),
                        help='whether use acl control')
    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.ACL_GID_KEY),
                        help='group id for media files')
    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.ACL_UID_KEY),
                        help='user id for media files')
    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.ACL_FILE_MOD_KEY),
                        help='expected file mod')
    parser.add_argument(ArgKeys.as_arg_key(ArgKeys.ACL_DIR_MOD_KEY),
                        help='expected dir mod')

    parser.add_argument('-c', '--config',
                        help='configure file path or a directory containing configure file named settings.yml')
    return parser

def get_config():
    parser = __make_parser__()
    args = parser.parse_args()
    config = Configure()
    config.set_by_config(args.config)
    config.set_by_obj(args)
    config.complete()
    return config