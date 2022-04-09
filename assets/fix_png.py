
##########################################################################################
# Use pngcrush to fix the  "libpng warning: iCCP: known incorrect sRGB profile" error
# on all .png images in folders within specified folder
# And/or use image magick for the same
# https://stackoverflow.com/questions/22745076/libpng-warning-iccp-known-incorrect-srgb-profile/29337595#29337595
##########################################################################################

import os

path = r"C:\Users\Gabriel\Documents\nqp2_\assets"  # path to all .png images

png_files = []

# clean file names as cant get cmd to work with spaces
# for dirpath, subdirs, files in os.walk(path):
#     for x in files:
#         os.rename(os.path.join(dirpath, x), os.path.join(dirpath, x.replace(" ", "")))

for dirpath, subdirs, files in os.walk(path):
    for x in files:
        if x.endswith(".png"):
            png_files.append(os.path.join(dirpath, x))

file = r"C:\Users\Gabriel\Downloads\pngcrush_1_8_11_w64.exe"  # pngcrush file

for name in png_files:
    #cmd = r'{} -ow -rem allb -reduce {}'.format(file, name)  # png crush
    cmd = f"magick mogrify -strip {name}"  # image magick
    os.system(cmd)
