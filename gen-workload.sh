#!/usr/bin/env bash

while true; do
  for f in $(seq 500); do
    dd if=/dev/zero of=/mnt/gluster/file_$f bs=64K count=320 oflag=direct
    sleep 5
  done
  for f in $(seq 500); do
    rm -f /mnt/gluster/file_$f
    sleep 20
  done
done
