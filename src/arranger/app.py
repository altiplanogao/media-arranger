import json
import logging
import os

from arranger.conf import ArrangeMode, DuplicateAction
from arranger.duplicate_handler import duplicate_droper, duplicate_mover, duplicate_skiper, duplicate_handle_counter
from arranger.file_op import FileCopier, FileMover
from analysor.others import SkipAnalysor
from analysor.analysors import analysors
from os import path
from utils import DirectoryIterator, FileHandlers, sha256_checksum


class MediaFileHandlers (FileHandlers):
    delete_able_files = ['.DS_Store'];
    def __init__(self, file_op, dest, doubts, respect_mtime=False, duplicate_counter=None):
        self.analysors = analysors(respect_mtime=respect_mtime)
        self.file_op = file_op
        self.dest = dest
        self.doubts = doubts
        self.duplicate_counter = duplicate_counter
        self.logger = logging.getLogger("file_process")
        self.file_hits = 0
        self.file_skip = 0
        self.file_handled = 0
        self.file_doubts = 0
        self.file_unhandled = 0
        return

    def __calc_doubt_dest__(self, factor):
        if self.doubts == None:
            return None
        src_noext, _ext = os.path.splitext(factor.src)

        hash = sha256_checksum(factor.src)
        bn = hash + _ext

        dst = os.path.join(self.doubts, bn)
        return dst

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
        if not path.isfile(file):
            raise RuntimeError('{0} should be a file'.format(file))
        self.file_hits += 1
        self.logger.info('[Skip: {1}, Handled:{2}, Doubts:{3}, Unhandled:{4}, No.{0}][{6}] File: {5}'
                         .format(self.file_hits, self.file_skip, self.file_handled, self.file_doubts, self.file_unhandled, file, str(self.duplicate_counter)))
        parser = self.analysors.get_analysor(file)
        if parser == None:
            self.file_skip += 1
            ga = self.analysors.get_generic()
            factor = ga.calc_factor(file)
            self.logger.info('{0} (size: {1}) skipped'.format(file, factor.file_size))
        else:
            if isinstance(parser, SkipAnalysor):
                self.logger.info('{0} skipped'.format(file))
                self.file_skip += 1
                return
            factor = parser.calc_factor(file)
            dates = factor.dates
            self.logger.info('[No.{0}] \n{1}'.format(self.file_hits, str(factor)))
            if self.__can_handle_factor__(factor):
                new_dst = self.__calc_dest__(factor=factor)
                self.file_op.op(src=file, dst=new_dst)
                self.file_handled += 1
            else:
                new_dst = self.__calc_doubt_dest__(factor=factor)
                if new_dst != None:
                    warning = 'DOUBT: {0} (size: {1}) moves to {2}'.format(factor.src, factor.file_size, new_dst)
                    self.logger.warning(warning)
                    self.file_op.op(src=file, dst=new_dst)
                    self.file_doubts += 1
                else:
                    warning = 'UNHANDLED: {0} (size: {1}) has no arrange info'.format(factor.src, factor.file_size)
                    self.logger.warning(warning)
                    self.file_unhandled += 1
                # return WarnAction(factor.src, msg=warning)
        return

    def on_dir_enter(self, file):
        return

    def on_dir_leave(self, file):
        contains_content = False
        for f in os.listdir(file):
            if f in MediaFileHandlers.delete_able_files:
                full_filename = path.join(file, f)
                self.logger.info("delete {0}".format(full_filename))
                os.remove(full_filename)
            else:
                contains_content = True
        if not contains_content:
            try:
                self.logger.info("delete {0}".format(file))
                os.rmdir(file)
                # shutil.rmtree(file, True)
            except Exception as e:
                self.logger.warning('delete failed due to {0}'.format(e))
        return None

class Application:
    def __init__(self, conf):
        self.conf = conf
        self.logger = logging.getLogger("app")
        self.dup_counter = duplicate_handle_counter()

        if conf.arrange_mode == ArrangeMode.MOVE:
            if conf.duplicate_action == DuplicateAction.SKIP:
                self.on_duplicate = duplicate_skiper(counter=self.dup_counter)
            elif conf.duplicate_action == DuplicateAction.DROP:
                self.on_duplicate = duplicate_droper(counter=self.dup_counter)
            elif conf.duplicate_action == DuplicateAction.MOVE:
                self.on_duplicate = duplicate_mover(conf.duplicate_dir,counter=self.dup_counter)
            else:
                raise RuntimeError("Duplication handler not set")
        else:
            self.on_duplicate = duplicate_skiper(counter=self.dup_counter)

        if conf.arrange_mode == ArrangeMode.COPY:
            self.file_op = FileCopier(acl_conf=conf.acl, on_duplicated=self.on_duplicate.op)
        elif conf.arrange_mode == ArrangeMode.MOVE:
            self.file_op = FileMover(acl_conf=conf.acl, on_duplicated=self.on_duplicate.op)
        else:
            raise RuntimeError("Arrange method not set")

    def run(self):
        self.logger.info("Configuration: {}".format((json.dumps(self.conf.to_dict(), ensure_ascii=False, indent=2))))

        mfh = MediaFileHandlers(self.file_op, dest=self.conf.dest, doubts=self.conf.doubts, respect_mtime=self.conf.respect_mtime , duplicate_counter=self.dup_counter)
        directory_iterator=DirectoryIterator(mfh)
        for src in self.conf.src:
            try:
                directory_iterator.iterate(file=src)
            except IOError as e:
                self.logger.error(str(e))
        self.logger.info('[Skip: {0}, Handled:{1}, Doubts:{2}, Unhandled:{3}, Total.{4}]'
                         .format(mfh.file_skip, mfh.file_handled, mfh.file_doubts, mfh.file_unhandled, mfh.file_hits))

        self.logger.info('Duplicates handled: [Skip: {0}, Move:{1}, Delete:{2}, Total.{3}]'
                         .format(self.dup_counter.skip(), self.dup_counter.move(), self.dup_counter.drop(), self.dup_counter.total()))
