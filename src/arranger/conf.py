from datetime import datetime
from enum import IntEnum
from os import path
from logging import config as logging_config
import argparse
import os
import yaml

class ArrangeMode(IntEnum):
    COPY = 1
    MOVE = 2
    NA = 0xFF

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, str):
        str = str.lower()
        if str == 'copy':
            return cls.COPY
        elif str == 'move':
            return cls.MOVE
        else:
            return cls.NA

class DuplicateAction(IntEnum):
    SKIP = 1
    DROP = 2
    MOVE = 3
    NA = 0xFF

    def __str__(self):
        return self.name

    @classmethod
    def from_str(cls, str):
        str = str.lower()
        if str == 'skip':
            return cls.SKIP
        elif str == 'drop':
            return cls.DROP
        elif str == 'move':
            return cls.MOVE
        else:
            return cls.NA

class AclConf:
    def __init__(self):
        self.chown = False
        self.chown_uid = -1
        self.chown_gid = -1
        self.file_mod = 0
        self.dir_mod = 0

class ArgKeys:
    SOURCE_KEY = 'source'
    DESTINATION_KEY = 'destination'
    DUPLICATE_DEST_DIR_KEY = 'duplicate_dest_dir'
    LOG_DIR_KEY = 'log_dir'

    ARRANGE_MODE_KEY = 'arrange_mode'
    ARRANGE_MODE_DEFAULT_VAL = ArrangeMode.COPY
    DUPLICATE_ACTION_KEY = 'duplicate_action'
    DUPLICATE_ACTION_DEFAULT_VAL = DuplicateAction.SKIP

    RESPECT_MTIME_KEY = 'respect_mtime'
    RESPECT_MTIME_DEFAULT_VAL = 'no'
    ACL_CHOWN_KEY = 'chown'
    ACL_CHOWN_DEFAULT_VAL = 'no'
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

class Configure:
    def __init__(self):
        self.src = []
        self.dest = None
        self.log_dir = '.'

        self.arrange_mode = ArgKeys.ARRANGE_MODE_DEFAULT_VAL
        self.duplicate_action = DuplicateAction.SKIP
        self.duplicate_dest_dir = None

        self.respect_mtime = 'no'
        self.acl = None

    @staticmethod
    def __boolean__(key, v):
        if isinstance(v, (bool)):
            return v
        elif isinstance(v, (str)):
            v = v.lower()
            if (v in ['yes', 'true']):
                return True
            elif (v in ['no', 'false']):
                return False
        raise Exception(u"Invalid boolean value '{1}' for key '{0}'".format(key, v))

    def set_log_dir(self, dir):
        if dir == None:
            return
        self.log_dir = dir

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
                    self.src = conf.get('source')
                    self.dest = conf.get('destination')
                    self.arrange_mode = ArrangeMode.from_str(conf.get('arrange_method', 'copy'))
                    self.duplicate_action = DuplicateAction.from_str(conf.get('on_duplicate', 'skip'))
                    self.set_log_dir(conf.get('log_dir', './logs'))
                    self.respect_mtime = Configure.__boolean__('respect_mtime', conf.get('respect_mtime', 'no'))
                    self.chown = Configure.__boolean__('chown', conf.get('chown', 'no'))
                except yaml.YAMLError as exc:
                    return False
            return True
        return False

    def set_by_args(self, args):
        if args.source:
            self.src = args.source
        if args.destination:
            self.dest = args.destination
        if args.arrange_method:
            self.arrange_mode = ArrangeMode.from_str(args.arrange_method)
        if args.on_duplicate:
            self.duplicate_action = DuplicateAction.from_str(args.on_duplicate)
        if args.respect_mtime:
            self.respect_mtime = Configure.__boolean__('respect_mtime', args.respect_mtime)
        if args.log_dir:
            self.set_log_dir(args.log_dir)
        return

    def complete(self):
        if self.arrange_mode == ArrangeMode.COPY:
            self.duplicate_action = DuplicateAction.SKIP
        now = datetime.now()
        nowstr = now.strftime('%Y%m%d_%H%M%S')

        if not path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        logging_conf_file = 'logging.yml'
        if path.isfile(logging_conf_file):
            with open(logging_conf_file, 'r') as stream:
                try:
                    conf = yaml.load(stream)
                    log_file = conf.get('handlers').get('file').get('filename')
                    full_log_file = path.join(self.log_dir, nowstr + '.log')
                    self.log_file = full_log_file
                    conf.get('handlers').get('file')['filename'] = full_log_file
                    logging_config.dictConfig(conf)
                except yaml.YAMLError as exc:
                    print(exc)


    def to_dict(self):
        return {
            'src' : self.src,
            'dest' : self.dest,
            'arrange_method' : str(self.arrange_mode),
            'on_duplicate' : str(self.duplicate_action),
            'respect_mtime' : self.respect_mtime,
            'log_file' : self.log_file
        }


def __make_parser__():
    parser = argparse.ArgumentParser(description='Arrange media files.')
    parser.add_argument('-s', '--source',
                        nargs='+',
                        help='set source directories')
    parser.add_argument('-d', '--destination',
                        help='set destination directory')
    parser.add_argument('--arrange-method',
                        choices=['copy', 'move'],
                        help='arrange by move or copy')
    parser.add_argument('--on-duplicate',
                        choices=['drop', 'skip'],
                        help='whether drop the source file on duplicated. Only works when "arrange-method" == "move"')
    parser.add_argument('--respect-mtime',
                        choices=['yes', 'no'],
                        help='whether use mtime on missing exif time')
    parser.add_argument('--log-dir', help='log directory')
    parser.add_argument('-c', '--config',
                        help='configure file path or a directory containing configure file named settings.yml')
    return parser

def parse_args():
    parser = __make_parser__()
    args = parser.parse_args()
    config = Configure()
    config.set_by_config(args.config)
    config.set_by_args(args)
    config.complete()
    return config