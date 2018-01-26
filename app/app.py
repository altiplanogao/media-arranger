import json
import shutil

import yaml
import argparse
import os
from os import path
from datetime import datetime
from enum import Enum

from app.arranger import MediaArranger, WarnAction, CopyAction
from app.file_copier import CopyMode, FileCopier
from app.media_parser.media_parser import media_parser
from app.media_parser.others import SkipParser
from app.utils import Global, FileHandlers, Logger, DirectoryIterator

class OnDuplicate(Enum):
    SKIP = 1
    DROP = 2
    NA = 0xFF

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, str):
        str = str.lower()
        if str == 'skip':
            return cls.SKIP
        elif str == 'drop':
            return cls.DROP
        else:
            return cls.NA

class Configure:
    def __init__(self):
        self.src = []
        self.dest = None
        self.arrange_method = CopyMode.COPY
        self.on_duplicate = OnDuplicate.SKIP
        self.respect_mtime = 'no'
        self.log_dir = '.'
        self.chown = False
        self.chown_uid = -1
        self.chown_gid = -1
        self.file_mod = 0
        self.dir_mod = 0

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
                    self.arrange_method = CopyMode.from_str(conf.get('arrange_method', 'copy'))
                    self.on_duplicate = OnDuplicate.from_str(conf.get('on_duplicate', 'skip'))
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
            self.arrange_method = CopyMode.from_str(args.arrange_method)
        if args.on_duplicate:
            self.on_duplicate = OnDuplicate.from_str(args.on_duplicate)
        if args.respect_mtime:
            self.respect_mtime = Configure.__boolean__('respect_mtime', args.respect_mtime)
        if args.log_dir:
            self.set_log_dir(args.log_dir)
        return

    def complete(self):
        if self.arrange_method == CopyMode.COPY:
            self.on_duplicate = OnDuplicate.SKIP
        now = datetime.now()
        nowstr = now.strftime('%Y%m%d_%H%M%S')

        if not path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.log_out = path.join(self.log_dir, "log_" + nowstr + "_out.log")
        self.log_err = path.join(self.log_dir, "log_" + nowstr + "_err.log")

    def to_dict(self):
        return {
            'src' : self.src,
            'dest' : self.dest,
            'arrange_method' : str(self.arrange_method),
            'on_duplicate' : str(self.on_duplicate),
            'respect_mtime' : self.respect_mtime,
            'log_out' : self.log_out,
            'log_err' : self.log_err
        }

class ArrangerFileHandlers(FileHandlers):
    ignorable_files = ['.DS_Store'];

    def __init__(self,conf, arranger):
        self.conf = conf
        self.copier = FileCopier(conf=conf, copy_mode=conf.arrange_method)
        self.arranger = arranger

    def on_file(self, file):
        Global.accum().total_pp()
        mp = media_parser(file)
        if (mp != None):
            if isinstance(mp, SkipParser):
                Global.logger().info_line('{0} skipped'.format(file))
                return
            factor = mp.calc_factor(file)
            Global.logger().info_line(str(factor))
            action = self.arranger.action_to_take(factor)
            if isinstance(action, WarnAction):
                Global.logger().error_line(action.msg)
                Global.accum().failed_pp()
            elif isinstance(action, CopyAction):
                check = self.copier.pre_copy(action.src, action.dst)
                if check[0] == FileCopier.DUPLICATED:
                    Global.logger().info_line('{0} exists with same content'.format(action.src))
                    self.on_duplicate_file(action.src)
                elif check[0] == FileCopier.REQUIRE_RENAME:
                    Global.logger().info_line('{0} name exists, save to {1}'.format(action.dst, check[1]))
                    result = self.copier.copy(action.src, check[1])
                    Global.logger().info_line('{0} -> {1} saved'.format(action.src, result))
                elif check[0] == FileCopier.READY_TO_COPY:
                    result = self.copier.copy(action.src, action.dst)
                    Global.logger().info_line('{0} -> {1} saved'.format(action.src, result))

                Global.accum().success_pp()
            else:
                raise ValueError('action type not implemented')
        else:
            Global.logger().error_line('Missing Media Parser for: %s' % (file))

    def on_duplicate_file(self, file):
        Global.accum().duplicates_pp()
        if self.conf.on_duplicate == OnDuplicate.DROP:
            os.remove(file)
            Global.logger().info_line('{0} dropped on duplicate'.format(file))
        return

    def on_dir_leave(self, file):
        contains_content = False
        for f in os.listdir(file):
            if f not in ArrangerFileHandlers.ignorable_files:
                contains_content = True
                break
        if not contains_content:
            shutil.rmtree(file, True)
        return None


class App:
    def __init__(self, argv):
        self.conf = App.parse_config(argv)

    @staticmethod
    def parse_config(argv):
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

        args = parser.parse_args()
        config = Configure()
        config.set_by_config(args.config)
        config.set_by_args(args)
        config.complete()

        return config

    def run(self):
        with Logger(self.conf.log_out, self.conf.log_err) as logger:
            Global.set_logger(logger)
            Global.logger().info_line("Configuration: %s\n" % (json.dumps(self.conf.to_dict(), ensure_ascii=False, indent=4)))
            arranger = MediaArranger(conf=self.conf)
            directory_iterator=DirectoryIterator(ArrangerFileHandlers(conf=self.conf, arranger=arranger))
            for src in self.conf.src:
                try:
                    directory_iterator.iterate(file=src)
                except IOError as e:
                    Global.logger().error_line(str(e))
            Global.logger().info_line('Result: {0}'.format(Global.accum()))
