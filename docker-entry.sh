#!/bin/bash

if [[ $1 == "bash" ]]; then
  /bin/bash
else
  echo Run CMD: python entry.py -c /appspace/config $@
  exec python entry.py -c /appspace/config $@
fi
