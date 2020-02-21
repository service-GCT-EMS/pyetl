import pdal

json = """
[
    {
        "filename":"entree/lidar/2050000_7274500_Lidar_15-16.laz"
    },
    {
        "type":"filters.range",
        "limits":"Classification[0:0]"
    },
    {
        "type":"filters.splitter",
        "length":"5",
        "origin_x":"2050000",
        "origin_y":"7274500"
    },
    {
        "resolution": 0.5,
        "radius": 0.6,
        "output_type":"count",
        "filename":"sortie/lidar/dalle_#.tif",
        "origin_x":"2050000",
        "origin_y":"7274500",
        "width":"100",
        "height":"100"
    }
]"""

pipeline = pdal.Pipeline(json)
pipeline.validate()  # check if our JSON and options were good
pipeline.loglevel = 8  # really noisy
count = pipeline.execute()
arrays = pipeline.arrays
metadata = pipeline.metadata
log = pipeline.log
