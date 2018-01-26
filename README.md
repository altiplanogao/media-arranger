# gy-media-arranger

Arrange media files according to creation time.

Media files are created with exif informations. (This tool uses [ExifTools](https://www.sno.phy.queensu.ca/~phil/exiftool/) under the hood)

Copy(or move) media files from source directory to destination directory (See sample configure [here](app/config/settings.yml) ).

The media file will be:
 * Renamed by creation time (a suffix added on conflict)
 * Grouped by month

For example:

If there is a jpg file created at 2018.01.25 12:34:56.
 * A new directory named "201801" will be created. Source image will be copy(or move) to the directory.
 * The jpg file will be assigned with a new file name: "20180125-123456.jpg".
 * If file "20180125-123456.jpg" with different content already placed in the directory, the new file name would be "20180125-123456(1).jpg", and so on.
 
## Use the tool:

### Method 1:
```
python3 entry.py -s SOURCE_DIR1 SOURCE_DIR2 -d DEST_DIR --arrange-method move --log-dir LOG_DIR -c CONFIG_FILE
```
For command helpp:
```
python3 entry.py -h
```

### Method 2:
```
docker run --rm -v SOURCE_DIR:/appspace/src -v DEST_DIR:/appspace/dst -v LOG_DIR:/appspace/logs -v CONFIG_DIR:/appspace/config altiplanogao/media-arranger
```
