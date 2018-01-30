import abc
import logging
import os
import shutil
from os import path
from utils import sha256_checksum, Global


class OpContext:
    def __init__(self, src ):
        self.src = src
        self.duplication = None
        self.dest = None
    def is_duplicated(self):
        return self.duplication != None

class __FileOpBase():
    def __init__(self, acl_conf, on_duplicated, hash_check = True, rename_pattern = '-%d'):
        self.acl_conf = acl_conf
        self.on_duplicated = on_duplicated
        self.hash_check = hash_check
        self.rename_pattern = rename_pattern
        self.action_count = 0
        self.logger = logging.getLogger('mover')

    def __determine_dest__(self, src, pref_dest):
        src_dir = path.dirname(src)
        src_bn = path.basename(src);
        src_bn_noext, src_ext = path.splitext(src_bn)

        dst_dir = path.dirname(pref_dest)
        dst_bn = path.basename(pref_dest);
        dst_bn_noext, dst_ext = path.splitext(dst_bn)

        op_ctx = OpContext(src)

        if path.exists(pref_dest):
            if self.hash_check:
                src_hash = sha256_checksum(src)
                siblings = []
                for sibling in os.listdir(dst_dir):
                    if sibling.startswith(dst_bn_noext) and sibling.endswith(dst_ext):
                        siblings.append(sibling)
                        sibling_hash = sha256_checksum(path.join(dst_dir, sibling))
                        if sibling_hash == src_hash:
                            op_ctx.duplication = path.join(dst_dir, sibling)
                            return op_ctx

            aimed = False
            id = 1
            while not aimed:
                new_dst_bn = dst_bn_noext + self.rename_pattern % (id) + dst_ext
                new_dst = path.join(dst_dir, new_dst_bn)
                if not path.exists(new_dst):
                    op_ctx.dest = new_dst
                    return op_ctx
                id += 1
            raise AssertionError('Error happens')
        else:
            op_ctx.dest = pref_dest
            return op_ctx

    def present_parent(self, file):
        parent = path.dirname(file)
        if not path.isdir(parent):
            self.mkdir(parent)

    def mkdir(self, dir):
        parent = path.dirname(dir)
        if not path.isdir(parent):
            self.mkdir(parent)
        os.mkdir(dir)
        if self.acl_conf:
            if self.acl_conf.chown:
                os.chown(dir, self.acl_conf.chown_uid, self.acl_conf.chown_gid)
            if self.acl_conf.dir_mod != 0:
                os.chmod(dir, self.acl_conf.dir_mod)

    def op(self, src, dst):
        op_ctx = self.__determine_dest__(src=src, pref_dest=dst)
        if op_ctx.is_duplicated():
            if self.on_duplicated != None:
                self.on_duplicated(src, op_ctx.duplication)
            else:
                raise RuntimeError('Duplication not handled')
            return None
        else:
            self.action_count += 1
            res = self.do_op(src = op_ctx.src, dst= op_ctx.dest)
            self.__set_acl__(file=op_ctx.dest)
            return res

    @abc.abstractmethod
    def do_op(self, src, dst):
        return

    def __set_acl__(self, file):
        if self.acl_conf:
            if self.acl_conf.chown:
                os.chown(file, self.conf.chown_uid, self.acl_conf.chown_gid)
            if self.acl_conf.file_mod != 0:
                os.chmod(file, self.acl_conf.file_mod)


class FileMover(__FileOpBase):
    def __init__(self, acl_conf, on_duplicated, hash_check = True):
        super().__init__(acl_conf, on_duplicated, hash_check)

    def do_op(self, src, dst):
        self.present_parent(dst)
        shutil.move(src=src, dst=dst)
        self.logger.info('move {0} -> {1}'.format(src, dst))
        return dst


class FileCopier(__FileOpBase):
    def __init__(self, acl_conf, on_duplicated, hash_check = True):
        super().__init__(acl_conf, on_duplicated, hash_check)

    def do_op(self, src, dst):
        self.present_parent(dst)
        shutil.copy(src=src, dst=dst)
        self.logger.info('copy {0} -> {1}'.format(src, dst))
        return dst

