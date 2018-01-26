#!/bin/bash
this_dir=`dirname $0`
pushd $this_dir
  this_dir=`pwd`
popd
EXIF_TOOL=Image-ExifTool

if [[ ! -d ''$EXIF_TOOL ]] ; then
  wget https://www.sno.phy.queensu.ca/~phil/exiftool/Image-ExifTool-10.75.tar.gz
  tar xzf Image-ExifTool-10.75.tar.gz
  mv Image-ExifTool-10.75 $EXIF_TOOL
#  rm Image-ExifTool-10.75.tar.gz
fi

if [[ ! -z $VIRTUAL_ENV ]] ; then
  sed -i 's|^PATH="$VIRTUAL_ENV/bin:.*$PATH"$|PATH="$VIRTUAL_ENV/bin:'$(echo $this_dir)'/Image-ExifTool:$PATH"|g' $VIRTUAL_ENV/bin/activate
fi

. $VIRTUAL_ENV/bin/activate
rm $this_dir/activate
ln -s $VIRTUAL_ENV/bin/activate $this_dir/activate
