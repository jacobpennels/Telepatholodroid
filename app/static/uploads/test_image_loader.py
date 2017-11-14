import javabridge
import bioformats
import os

javabridge.start_vm(class_path=bioformats.JARS)

ImageReader = bioformats.formatreader.make_image_reader_class()
reader = ImageReader()
reader.setId('HEsample.jp2')
print(str(reader.getSizeX()) + ", " + str(reader.getSizeY()))

test = reader.openBytesXYWH(0, 0, 0, 5, 5)

javabridge.kill_vm()
