#!/usr/bin/env bash

NUMFILES=400
NUMBLOCKS=640

echo "Checking for volume to write to"
MOUNTED=$(mountpoint -q /mnt/glusterfs ; echo $?)
if [ "$MOUNTED" -eq 1 ]; then
  echo "you need to mount a volume first to /mnt/glusterfs"
  exit
fi

echo "- volume OK, starting the workload"
while true; do

  for f in $(seq ${NUMFILES}); do
    dd if=/dev/zero of=/mnt/glusterfs/file_$f bs=64K count=${NUMBLOCKS} oflag=direct
    sleep 5
  done

  for f in $(seq ${NUMFILES}); do
    rm -f /mnt/glusterfs/file_$f
    sleep 20
  done

done