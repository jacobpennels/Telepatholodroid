import openslide
import PIL
from openslide import deepzoom

osr = openslide.OpenSlide('test_img_1.svs')
thumb = osr.get_thumbnail((250, 250))

dz = deepzoom.DeepZoomGenerator(osr)
print(dz.tile_count)
print(dz.level_tiles)
print(dz.get_dzi('png'))

img1 = dz.get_tile(9, (0, 0))

thumb.save("thmb_test.png", "png")
img1.show()

