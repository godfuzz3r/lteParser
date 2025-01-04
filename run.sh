#!/bin/bash
set -x
# hack but works
xhost +
docker run \
  -it --rm --privileged \
  --network=host \
  --cap-add=ALL \
  --ulimit nofile=65535:65535 \
  --ulimit nice=0:0 \
  --ulimit memlock=-1:-1 \
  -e PULSE_SERVER=unix:/run/user/1000/pulse/native \
  -v /dev/bus/usb:/dev/bus/usb \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v /lib/modules:/lib/modules \
  -v ./vol:/vol \
  -e DISPLAY=unix$DISPLAY \
  -u root \
  -v /run/user/1000/pulse:/run/user/1000/pulse \
  -v ./srsRAN_4G:/src \
  lte-sib-parser-main-worker
