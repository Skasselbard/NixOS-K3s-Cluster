#!/bin/bas

sudo echo ''

if [ -z ${1+x} ]; then echo "first parameter should be the usb drive path (/dev/sdx)"; exit 1; fi

if ! [ -e ${1} ]; then echo "device not found"; exit 1; fi

# sudo mkdosfs -v -I ${1} -F 32
sudo dd if=nixos/iso/nixos.iso of=${1} bs=4M conv=fsync status=progress
sync
