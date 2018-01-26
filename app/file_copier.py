import shutil
import os
from enum import Enum
from os import path

from app.utils import sha256_checksum

class CopyMode(Enum):
    COPY = 1
    MOVE = 2
    NA = 0xFF

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, str):
        str = str.lower()
        if str == 'copy':
            return cls.COPY
        elif str == 'move':
            return cls.MOVE
        else:
            return cls.NA

class FileCopier:
    DUPLICATED = 'duplicated'
    REQUIRE_RENAME = 'require.rename'
    READY_TO_COPY = 'ready.to.copy'

    def __init__(self, conf = None,
                 copy_mode = CopyMode.COPY, rename_pattern = '(%d)', duplicate_handler = None):
        self.conf = conf
        self.copy_mode = copy_mode
        self.rename_pattern = rename_pattern
        self.duplicate_handler = duplicate_handler

    def pre_copy(self, src, dst):
        src_dir = path.dirname(src)
        src_bn = path.basename(src);
        src_bn_noext, src_ext = path.splitext(src_bn)

        dst_dir = path.dirname(dst)
        dst_bn = path.basename(dst);
        dst_bn_noext, dst_ext = path.splitext(dst_bn)

        if path.exists(dst):
            duplicated = False
            src_hash = sha256_checksum(src)
            siblings = []
            for sibling in os.listdir(dst_dir):
                if sibling.startswith(dst_bn_noext) and sibling.endswith(dst_ext):
                    siblings.append(sibling)
                    sibling_hash = sha256_checksum(path.join(dst_dir, sibling))
                    if sibling_hash == src_hash:
                        duplicated = True
                        break
            if duplicated:
                return [FileCopier.DUPLICATED]
            aimed = False
            id = 1
            while not aimed:
                new_dst_bn = dst_bn_noext + self.rename_pattern % (id) + dst_ext
                new_dst = path.join(dst_dir, new_dst_bn)
                if not path.exists(new_dst):
                    dst = new_dst
                    return [FileCopier.REQUIRE_RENAME, dst]
                id += 1
        return [FileCopier.READY_TO_COPY]

    # return the real dest
    def copy(self, src, dst):
        src_dir = path.dirname(src)
        src_bn = path.basename(src);
        src_bn_noext, src_ext = path.splitext(src_bn)

        dst_dir = path.dirname(dst)
        dst_bn = path.basename(dst);
        dst_bn_noext, dst_ext = path.splitext(dst_bn)

        if not path.isdir(dst_dir):
            self.mkdir(dst_dir)

        self.__do_copy__(src, dst)
        if self.conf:
            if self.conf.chown:
                os.chown(dst, self.conf.chown_uid, self.conf.chown_gid)
            if self.conf.file_mod != 0:
                os.chmod(dst, self.conf.file_mod)
        return dst

    def mkdir(self, dir):
        parent = path.dirname(dir)
        if not path.isdir(parent):
            self.mkdir(parent)
        os.mkdir(dir)
        if self.conf:
            if self.conf.chown:
                os.chown(dir, self.conf.chown_uid, self.conf.chown_gid)
            if self.conf.dir_mod != 0:
                os.chmod(dir, self.conf.dir_mod)

    def __do_copy__(self, src, dst):
        if self.copy_mode == CopyMode.MOVE:
            shutil.move(src=src, dst=dst)
        elif self.copy_mode == CopyMode.COPY:
            shutil.copy(src=src, dst=dst)


