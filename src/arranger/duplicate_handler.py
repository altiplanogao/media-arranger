import logging
import os
from os import path

from arranger.file_op import FileMover

class duplicate_handle_counter:
    def __init__(self):
        self._skip = 0
        self._drop = 0
        self._move = 0

    def skip(self):
        return self._skip

    def drop(self):
        return self._drop

    def move(self):
        return self._move

    def total(self):
        return self._skip + self._drop + self._move


class duplicate_handler:
    def __init__(self, counter = duplicate_handle_counter()):
        self.logger = logging.getLogger("file_process")
        self.counter = counter

class duplicate_skiper(duplicate_handler):
    def __init__(self, counter = duplicate_handle_counter()):
        super().__init__(counter = counter)
    def op(self, src, duplication):
        self.logger.info('Duplicate skipped : {0}, {1}'.format(src, duplication))
        self.counter._skip += 1
        return

class duplicate_mover(duplicate_handler):
    def __init__(self, dest_dir, counter = duplicate_handle_counter()):
        super().__init__(counter = counter)
        self.dest_dir = dest_dir
        self.mover = FileMover(acl_conf=None, on_duplicated=None, hash_check=False)

    def op(self, src, duplication):
        src_dir = path.dirname(src)
        src_bn = path.basename(src);
        self.mover.op(src=src, dst=path.join(self.dest_dir,src_bn))
        self.counter._move += 1
        self.logger.info('Duplicate move : {0}, {1}'.format(src, duplication))


class duplicate_droper(duplicate_handler):
    def __init__(self, counter = duplicate_handle_counter()):
        super().__init__(counter = counter)

    def op(self, src, duplication):
        os.remove(src)
        self.counter._drop += 1
        self.logger.info('Duplication drop : {0}(DROPPED) == {1}'.format(src, duplication))
