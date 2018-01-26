import os.path
import os

from app.file_copier import FileCopier
from app.utils import Global


class Arranger:
    ignorable_files = ['.DS_Store'];
    def __init__(self, dest):
        self.dest = dest
    def arrange(self, factor):
        return None

class MediaArranger(Arranger):
    def __init__(self, conf):
        Arranger.__init__(self, dest = conf.dest)
        self.move_mode = False
        self.drop_duplicate = False
        if conf.arrange_method == 'move':
            self.move_mode = True
        if self.move_mode and conf.on_duplicate == 'drop':
            self.drop_duplicate = True
        self.copier = FileCopier(conf=conf, move_mode=self.move_mode,
                                 duplicate_handler=self.__duplicate_callback__)

    def __duplicate_callback__(self, src):
        Global.accum().duplicates_pp()
        if self.drop_duplicate:
            os.remove(src)
            Global.logger().info_line('{0} dropped on duplicate'.format(src))
        return

    def arrange(self, factor):
        if self.__can_handle_factor__(factor):
            new_dst = self.__calc_dest__(factor = factor)
            result = self.copier.copy(factor.src, new_dst)
            Global.logger().info_line('{0} -> {1}'.format(factor.src, result))
            Global.accum().success_pp()
        else:
            Global.logger().error_line('{0} (size: {1}) not handled'.format(factor.src, factor.file_size))
            Global.accum().failed_pp()

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

