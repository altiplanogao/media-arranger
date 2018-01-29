#!/usr/bin/env python

import sys

sys.path.remove('/usr/local/lib/python2.7/dist-packages')

import utils
from arranger.app import Application
from arranger.conf import *

def main(argv):
    # sys.setdefaultencoding('utf-8')
    conf = get_config()

    app = Application(conf=conf)
    utils.Global.__APP__ = app
    app.run()

if __name__ == '__main__':
    main(sys.argv)