import json
import logging
import os
import shutil

from arranger.conf import ArrangeMode, DuplicateAction
from arranger.duplicate_handler import duplicate_droper, duplicate_mover, duplicate_skiper
from arranger.file_op import FileCopier, FileMover
from analysor.others import SkipAnalysor
from analysor.analysors import get_analysor
from utils import Global, DirectoryIterator, FileHandlers

class MediaFileHandlers (FileHandlers):
    ignorable_files = ['.DS_Store'];
    def __init__(self, file_op, dest):
        self.file_op = file_op
        self.dest = dest
        self.logger = logging.getLogger("file_process")
        return

    def __calc_dest__(self, factor):
        src_noext, _ext = os.path.splitext(factor.src)

        dt = factor.datetime
        bn = dt.strftime('%Y%m%d-%H%M%S') + _ext

        dest_dir = os.path.join(self.dest, dt.strftime('%Y%m'))
        dst = os.path.join(dest_dir, bn)
        return dst

    def __can_handle_factor__(self, factor):
        if len(factor.warning) > 0:
            self.logger.error('{0} [WARNING] '.format(factor.src))
            for k, v in factor.warning.items():
                self.logger.error('{0} : {1}'.format(k, v))
            return False
        return factor.datetime != None

    def on_file(self, file):
        parser = get_analysor(file)
        if parser != None:
            if isinstance(parser, SkipAnalysor):
                self.logger.info('{0} skipped'.format(file))
                return
            factor = parser.calc_factor(file)
            self.logger.info(str(factor))
            if self.__can_handle_factor__(factor):
                new_dst = self.__calc_dest__(factor=factor)
                self.file_op.op(src=file, dst=new_dst)
            else:
                warning = '{0} (size: {1}) not handled'.format(factor.src, factor.file_size)
                self.logger.warning(warning)
                # return WarnAction(factor.src, msg=warning)


    def on_dir_leave(self, file):
        contains_content = False
        for f in os.listdir(file):
            if f not in MediaFileHandlers.ignorable_files:
                contains_content = True
                break
        if not contains_content:
            shutil.rmtree(file, True)
        return None

class Application:
    def __init__(self, conf):
        self.conf = conf
        self.logger = logging.getLogger("app")

        if conf.on_duplicate == DuplicateAction.SKIP:
            self.on_duplicate = duplicate_skiper()
        elif conf.on_duplicate == DuplicateAction.DROP:
            self.on_duplicate = duplicate_droper()
        elif conf.on_duplicate == DuplicateAction.MOVE:
            self.on_duplicate = duplicate_mover(conf.duplicate_dir)
        else:
            raise RuntimeError("Duplication handler not set")
        if conf.arrange_method == ArrangeMode.COPY:
            self.file_op = FileCopier(acl_conf=conf.acl, on_duplicated=self.on_duplicate.op)
        elif conf.arrange_method == ArrangeMode.MOVE:
            self.file_op = FileMover(acl_conf=conf.acl, on_duplicated=self.on_duplicate.op)
        else:
            raise RuntimeError("Arrange method not set")

    def run(self):
        self.logger.info("Configuration: {}".format((json.dumps(self.conf.to_dict(), ensure_ascii=False, indent=2))))

        directory_iterator=DirectoryIterator(MediaFileHandlers(self.file_op, self.conf.dest))
        for src in self.conf.src:
            try:
                directory_iterator.iterate(file=src)
            except IOError as e:
                Global.logger().error_line(str(e))
        Global.logger().info_line('Result: {0}'.format(Global.accum()))
