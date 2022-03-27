
##########################################################################################
# Use pngcrush to fix the  "libpng warning: iCCP: known incorrect sRGB profile" error
# on all .png images in folders within specified folder
# https://stackoverflow.com/questions/22745076/libpng-warning-iccp-known-incorrect-srgb-profile/29337595#29337595
##########################################################################################

import os

path = r"C:\Users\Gabriel\Documents\nqp2_\assets"  # path to all .png images

png_files = []

for dirpath, subdirs, files in os.walk(path):
    for x in files:
        if x.endswith(".png"):
            png_files.append(os.path.join(dirpath, x))

file = r"C:\Users\Gabriel\Downloads\pngcrush_1_8_11_w64.exe"  # pngcrush file

for name in png_files:
    cmd = r'{} -ow -rem allb -reduce {}'.format(file, name)
    os.system(cmd)
