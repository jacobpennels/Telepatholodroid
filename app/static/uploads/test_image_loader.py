import openslide
import PIL
from openslide import deepzoom
import os
import shutil
import json

# Work out correct path
if os.path.isdir('test'):
    shutil.rmtree('test')
os.makedirs('test')
path = os.path.join(os.getcwd(), 'test')
print(path)

# Open image and then save the thumbnail image
osr = openslide.OpenSlide('test_img_1.svs')
#thumb = osr.get_thumbnail((250, 250))
#thumb.save(path + "/thumb.png", "png")
print(osr.dimensions)

dz = deepzoom.DeepZoomGenerator(osr)

info = {}
print(len(dz.level_dimensions))
print(len(dz.level_tiles))
for i, d in enumerate(dz.level_dimensions):
    tiles = dz.level_tiles[i]
    info['level_' + str(i)] = [d[0], d[1], tiles[0], tiles[1]]

print(info)
print(json.dumps(info))
with open("dimensions.json", 'w') as f:
    f.write(json.dumps(info))


