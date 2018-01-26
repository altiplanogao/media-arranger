import os.path
import os
from enum import Enum

from app.utils import Global

class Actions(Enum):
    NA = 0
    COPY =1
    WARN = 2
    SKIP=3

class Action:
    def __init__(self, src):
        self.src = src
    def action(self):
        return Actions.NA

class CopyAction(Action):
    def __init__(self, src, dst):
        Action.__init__(self, src = src)
        self.dst = dst
    def action(self):
        return Actions.COPY
class WarnAction(Action):
    def __init__(self, src, msg):
        Action.__init__(self, src = src)
        self.msg = msg

class MediaArranger():
    def __init__(self, conf):
        self.conf = conf
        self.dest = conf.dest

    def action_to_take(self, factor):
        if self.__can_handle_factor__(factor):
            new_dst = self.__calc_dest__(factor = factor)
            return CopyAction(factor.src, new_dst)
        else:
            warning = '{0} (size: {1}) not handled'.format(factor.src, factor.file_size)
            return WarnAction(factor.src, msg=warning)

    def __calc_dest__(self, factor):
        src_noext, _ext = os.path.splitext(factor.src)

        dt = factor.datetime
        bn = dt.strftime('%Y%m%d-%H%M%S') + _ext

        dest_dir = os.path.join(self.dest, dt.strftime('%Y%m'))
        dst = os.path.join(dest_dir, bn)
        return dst

    def __can_handle_factor__(self, factor):
        if len(factor.warning) > 0:
            Global.logger().error('{0} [WARNING] '.format(factor.src))
            for k, v in factor.warning.items():
                Global.logger().error('{0} : {1}'.format(k, v))
            Global.logger().error_line('')
            return False
        return factor.datetime != None

