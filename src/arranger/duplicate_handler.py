import logging
import os
from os import path

from arranger.file_op import FileMover

class duplicate_skiper:
    def __init__(self):
        self.logger = logging.getLogger("file_process")
    def op(self, src, duplication):
        self.logger.info('duplication skipped : {0} == {1}'.format(src, duplication))
        return

class duplicate_mover:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.mover = FileMover(acl_conf=None, on_duplicated=None, hash_check=False)

    def op(self, src, duplication):
        src_dir = path.dirname(src)
        src_bn = path.basename(src);
        self.mover.op(src=src, dst=path.join(self.dest_dir,src_bn))

class duplicate_droper:
    def __init__(self):
        return

    def op(self, src, duplication):
        self.logger.info('duplication : {0} == {1}'.format(src, duplication))
        os.remove(src)
