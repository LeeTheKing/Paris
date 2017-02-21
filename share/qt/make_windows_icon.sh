#!/bin/bash
# create multiresolution windows icon
ICON_SRC=../../src/qt/res/icons/Paris.png
ICON_DST=../../src/qt/res/icons/Paris.ico
convert ${ICON_SRC} -resize 16x16 Paris-16.png
convert ${ICON_SRC} -resize 32x32 Paris-32.png
convert ${ICON_SRC} -resize 48x48 Paris-48.png
convert Paris-16.png Paris-32.png Paris-48.png ${ICON_DST}

