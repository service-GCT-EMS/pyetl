from osgeo import gdal

gtif = gdal.Open("sortie/lidar/dalle_1.tiff")
print(gtif.GetMetadata())
