FROM python:3.4-slim

RUN mkdir -p /appspace/config
ADD ./app/config/settings.yml /appspace/config
VOLUME ["/appspace/src", "/appspace/dst", "/appspace/logs", "/appspace/config"]

ARG EXIF_TOOL_URL=https://www.sno.phy.queensu.ca/~phil/exiftool/Image-ExifTool-10.76.tar.gz
ADD ${EXIF_TOOL_URL} /
RUN tar xzf /Image-ExifTool-10.76.tar.gz
ENV PATH "/Image-ExifTool-10.76:${PATH}"

ADD . /media-arranger
RUN pip install --trusted-host pypi.python.org -r /media-arranger/requirements.txt

WORKDIR /media-arranger
CMD ["python", "entry.py", "-s", "/appspace/src", "-d", "/appspace/dst", "--log-dir", "/appspace/logs", "-c", "/appspace/config"]
