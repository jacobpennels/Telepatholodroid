import openslide
import PIL
from openslide import deepzoom
import os
import shutil

# Work out correct path
if os.path.isdir('test'):
    shutil.rmtree('test')
os.makedirs('test')
path = os.path.join(os.getcwd(), 'test')
print(path)

# Open image and then save the thumbnail image
osr = openslide.OpenSlide('test_img_1.svs')
thumb = osr.get_thumbnail((250, 250))
thumb.save(path + "/thumb.png", "png")
print(osr.dimensions)

dz = deepzoom.DeepZoomGenerator(osr)

for i, l in enumerate(dz.level_tiles):
    dir_name = path + '/level_' + str(i)
    os.makedirs(dir_name)
    print(i)
    for x in range(l[0]):
        for y in range(l[1]):
            img = dz.get_tile(i, (x, y))
            img.save(dir_name + '/tile_' + str(x) + '_' + str(y) + '.png')


