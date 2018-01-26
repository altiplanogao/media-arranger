#!/usr/bin/env python

import sys

from app import utils
from app.app import App


def main(argv):
    # sys.setdefaultencoding('utf-8')
    app = App(argv)
    utils.Global.__APP__ = app
    app.run()

if __name__ == '__main__':
    main(sys.argv)