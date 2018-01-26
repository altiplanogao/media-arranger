import os
import os.path as path
import sys
import hashlib

__all__ = [
    'FileHandlers', 'DirectoryIterator', 'Global'
]

class FileHandlers:
    def on_file(self, file):
        return
    def on_duplicate_file(self, file):
        return
    def on_dir_enter(self, file):
        return
    def on_dir_leave(self, file):
        return

class DirectoryIterator:
    def __init__(self, file_handlers = FileHandlers()):
        self.file_handlers = file_handlers

    def iterate(self, file):
        if path.isfile(file):
            self.file_handlers.on_file(file)
        elif path.isdir(file):
            self.file_handlers.on_dir_enter(file)
            for child in sorted(os.listdir(file)):
                self.iterate(path.join(file, child))
            self.file_handlers.on_dir_leave(file)
        elif not path.exists(file):
            raise IOError('file not exist: "%s"' % file)

class Logger:
    def __init__(self, out, err):
        self.out = out
        self.err = err
        self.out_file = None
        self.err_file = None

    def __enter__(self):
        self.out_file = open(self.out, mode='a', encoding='utf-8')
        self.err_file = open(self.err, mode='a', encoding='utf-8')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.out_file.close()
        self.err_file.close()

    def info_line(self, line):
        line += '\n'
        self.info(line)

    def info(self, line):
        sys.stdout.write(line)
        self.out_file.write(line)
        self.out_file.flush()

    def error_line(self, line):
        line += '\n'
        self.error(line)

    def error(self, line):
        sys.stderr.write(line)
        self.err_file.write(line)
        self.err_file.flush()

class Accum:
    def __init__(self):
        self.__success__ = 0
        self.__failed__ = 0
        self.__duplicates__ = 0
        self.__total__ = 0

    def __str__(self):
        return 'suc: {0}, fail: {1}, dup: {2}, total: {3}'.format(self.__success__,
                                                                   self.__failed__,
                                                                   self.__duplicates__,
                                                                   self.__total__)

    def total_pp(self):
        self.__total__ += 1

    def success_pp(self):
        self.__success__ += 1

    def failed_pp(self):
        self.__failed__ += 1

    def duplicates_pp(self):
        self.__duplicates__ += 1


    def total_count(self):
        return self.__total__

    def success_count(self):
        return self.__success__

    def failed_count(self):
        return self.__failed__

    def duplicates_count(self):
        return self.__duplicates__

class Global:
    __LOGGER__ = None
    __APP__ = None
    __accum__ = Accum()

    @staticmethod
    def logger():
        return Global.__LOGGER__

    @staticmethod
    def set_logger(logger):
        Global.__LOGGER__ = logger

    @staticmethod
    def accum():
        return Global.__accum__

def distinct_list(list):
    distincted = []
    for v in list:
        if len(distincted) == 0:
            distincted.append(v)
        elif v != distincted[len(distincted) - 1]:
            distincted.append(v)
    return distincted

def sha256_checksum(filename, block_size = 65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()
