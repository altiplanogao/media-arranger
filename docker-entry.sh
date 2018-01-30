#!/bin/bash

if [[ $1 == "bash" ]]; then
  /bin/bash
else
  echo Run CMD: $@
  exec $@
fi
