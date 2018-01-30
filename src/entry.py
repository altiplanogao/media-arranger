#!/usr/bin/env python

import sys

#it seems that on some machine, python2 path would cause library conflict
p2path = list(x for x in sys.path if x.count('python2') > 0)
for p in p2path:
    sys.path.remove(p)

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