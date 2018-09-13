"""
shapefile.py
Provides read and write support for ESRI Shapefiles.
author: jlawhead<at>geospatialpython.com
date: 20140507
version: 1.2.1
Compatible with Python versions 2.4-3.x
version changelog: Fixed u() to just return the byte sequence on exception
"""

__version__ = "1.2.1"

from struct import pack, unpack, calcsize, error
import os
import sys
import time
import array
#import tempfile
#import itertools

#
# Constants for shape types
NULL = 0
POINT = 1
POLYLINE = 3
POLYGON = 5
MULTIPOINT = 8
POINTZ = 11
POLYLINEZ = 13
POLYGONZ = 15
MULTIPOINTZ = 18
POINTM = 21
POLYLINEM = 23
POLYGONM = 25
MULTIPOINTM = 28
MULTIPATCH = 31

PYTHON3 = sys.version_info[0] == 3

def b(v):
    if PYTHON3:
        if isinstance(v, str):
            # For python 3 encode str to bytes.
            return v.encode('utf-8')
        elif isinstance(v, bytes):
            # Already bytes.
            return v
        else:
            # Error.
            raise Exception('Unknown input type')
    else:
        # For python 2 assume str passed in and return str.
        return v

def u(v):
    if PYTHON3:
        # try/catch added 2014/05/07
        # returned error on dbf of shapefile
        # from www.naturalearthdata.com named
        # "ne_110m_admin_0_countries".
        # Just returning v as is seemed to fix
        # the problem.  This function could
        # be condensed further.
        try:
            if isinstance(v, bytes):
                # For python 3 decode bytes to str.
                return v.decode('cp1252')
            elif isinstance(v, str):
          # Already str.
                return v
            else:
      # Error.
                raise Exception('Unknown input type')
        except:
            v2 = ""
#           for b in v:
#              v2=v2+(b.decode('cp1252'))
            print(" shp: erreur de decodage", v, v2)
            v = v2
            return v2
    else:
        # For python 2 assume str passed in and return str.
        return v

class _Array(array.array):
    """Converts python tuples to lits of the appropritate type.
    Used to unpack different shapefile header parts."""
    def __repr__(self):
        return str(self.tolist())

def signed_area(coords):
    """Return the signed area enclosed by a ring using the linear time
    algorithm at http://www.cgafaq.info/wiki/Polygon_Area. A value >= 0
    indicates a counter-clockwise oriented ring.
    """
    xs, ys = list(map(list, list(zip(*coords))))
    xs.append(xs[1])
    ys.append(ys[1])
    return sum(xs[i]*(ys[i+1]-ys[i-1]) for i in range(1, len(coords)))/2.0

class _Shape:
    def __init__(self, shapeType=None):
        """Stores the geometry of the different shape types
        specified in the Shapefile spec. Shape types are
        usually point, polyline, or polygons. Every shape type
        except the "Null" type contains points at some level for
        example verticies in a polygon. If a shape type has
        multiple shapes containing points within a single
        geometry record then those shapes are called parts. Parts
        are designated by their starting index in geometry record's
        list of shapes."""
        self.shapeType = shapeType
        self.points = []

    @property
    def __geo_interface__(self):
        if self.shapeType in [POINT, POINTM, POINTZ]:
            return {'type': 'Point',
                    'coordinates': tuple(self.points[0])
                   }
        elif self.shapeType in [MULTIPOINT, MULTIPOINTM, MULTIPOINTZ]:
            return {'type': 'MultiPoint',
                    'coordinates': tuple([tuple(p) for p in self.points])
                   }
        elif self.shapeType in [POLYLINE, POLYLINEM, POLYLINEZ]:
            if len(self.parts) == 1:
                return {'type': 'LineString',
                        'coordinates': tuple([tuple(p) for p in self.points])
                       }
            else:
                pstart = None
                coordinates = []
                for part in self.parts:
                    if pstart is None:
                        pstart = part
                        continue
                    else:
                        coordinates.append(tuple([tuple(p) for p in self.points[pstart:part]]))
                        pstart = part
                else:
                    coordinates.append(tuple([tuple(p) for p in self.points[part:]]))
                return {'type': 'MultiLineString',
                        'coordinates': tuple(coordinates)
                       }
        elif self.shapeType in [POLYGON, POLYGONM, POLYGONZ]:
            if len(self.parts) == 1:
                return {'type': 'Polygon',
                        'coordinates': (tuple([tuple(p) for p in self.points]),)
                       }
            else:
                pstart = None
                coordinates = []
                for part in self.parts:
                    if pstart is None:
                        pstart = part
                        continue
                    else:
                        coordinates.append(tuple([tuple(p) for p in self.points[pstart:part]]))
                        pstart = part
                else:
                    coordinates.append(tuple([tuple(p) for p in self.points[part:]]))
                polys = []
                poly = [coordinates[0]]
                for coord in coordinates[1:]:
                    if signed_area(coord) < 0:
                        polys.append(poly)
                        poly = [coord]
                    else:
                        poly.append(coord)
                polys.append(poly)
                if len(polys) == 1:
                    return {'type': 'Polygon',
                            'coordinates': tuple(polys[0])
                           }
                elif len(polys) > 1:
                    return {'type': 'MultiPolygon',
                            'coordinates': polys
                           }

class _ShapeRecord:
    """A shape object of any type."""
    def __init__(self, shape=None, record=None):
        self.shape = shape
        self.record = record

class ShapefileException(Exception):
    """An exception to handle shapefile specific problems."""
    pass

class Reader:
    """Reads the three files of a shapefile as a unit or
    separately.  If one of the three files (.shp, .shx,
    .dbf) is missing no exception is thrown until you try
    to call a method that depends on that particular file.
    The .shx index file is used if available for efficiency
    but is not required to read the geometry from the .shp
    file. The "shapefile" argument in the constructor is the
    name of the file you want to open.

    You can instantiate a Reader without specifying a shapefile
    and then specify one later with the load() method.

    Only the shapefile headers are read upon loading. Content
    within each file is only accessed when required and as
    efficiently as possible. Shapefiles are usually not large
    but they can be.
    """
    def __init__(self, *args, **kwargs):
        self.shp = None
        self.shx = None
        self.dbf = None
        self.shapeName = "Not specified"
        self._offsets = []
        self.shpLength = None
        self.numRecords = None
        self.recFmt = None
        self.fields = []
        self.bbox = None
        self.measure = None
        self.elevation = None
        self.__dbfHdrLength = 0
        # See if a shapefile name was passed as an argument
        if args:
            self.load(args[0])
            return
        if "shp" in list(kwargs.keys()):
            if hasattr(kwargs["shp"], "read"):
                self.shp = kwargs["shp"]
                if hasattr(self.shp, "seek"):
                    self.shp.seek(0)
            if "shx" in list(kwargs.keys()):
                if hasattr(kwargs["shx"], "read"):
                    self.shx = kwargs["shx"]
                    if hasattr(self.shx, "seek"):
                        self.shx.seek(0)
        if "dbf" in list(kwargs.keys()):
            if hasattr(kwargs["dbf"], "read"):
                self.dbf = kwargs["dbf"]
                if hasattr(self.dbf, "seek"):
                    self.dbf.seek(0)
        if self.shp or self.dbf:
            self.load()
        else:
            raise ShapefileException("Shapefile Reader requires a shapefile or file-like object.")

    def load(self, shapefile=None):
        """Opens a shapefile from a filename or file-like
        object. Normally this method would be called by the
        constructor with the file object or file name as an
        argument."""
        if shapefile:
            (shapeName, ext) = os.path.splitext(shapefile)
            self.shapeName = shapeName
            try:
                if ext.isupper():
                    self.shp = open("%s.SHP" % shapeName, "rb")
                else:
                    self.shp = open("%s.shp" % shapeName, "rb")
            except IOError:
                raise ShapefileException("Unable to open %s.shp" % shapeName)
            try:
                if ext.isupper():
                    self.shx = open("%s.SHX" % shapeName, "rb")
                else:
                    self.shx = open("%s.shx" % shapeName, "rb")
            except IOError:
                raise ShapefileException("Unable to open %s.shx" % shapeName)
            try:
                if ext.isupper():
                    self.dbf = open("%s.DBF" % shapeName, "rb")
                else:
                    self.dbf = open("%s.dbf" % shapeName, "rb")
            except IOError:
                raise ShapefileException("Unable to open %s.dbf" % shapeName)
        if self.shp:
            self.__shpHeader()
        if self.dbf:
            self.__dbfHeader()

    def __getFileObj(self, f):
        """Checks to see if the requested shapefile file object is
        available. If not a ShapefileException is raised."""
        if not f:
            raise ShapefileException("Shapefile Reader requires a shapefile or file-like object.")
        if self.shp and self.shpLength is None:
            self.load()
        if self.dbf and not self.fields == 0:
            self.load()
        return f

    def __restrictIndex(self, i):
        """Provides list-like handling of a record index with a clearer
        error message if the index is out of bounds."""
        if self.numRecords:
            rmax = self.numRecords - 1
            if abs(i) > rmax:
                raise IndexError("Shape or Record index out of range.")
            if i < 0:
                i = list(range(self.numRecords))[i]
        return i

    def __shpHeader(self):
        """Reads the header information from a .shp or .shx file."""
        if not self.shp:
            raise ShapefileException("""Shapefile Reader requires a
                                     shapefile or file-like object.
                                     (no shp file found)""")
        shp = self.shp
        # File length (16-bit word * 2 = bytes)
        shp.seek(24)
        self.shpLength = unpack(">i", shp.read(4))[0] * 2
        # Shape type
        shp.seek(32)
        self.shapeType = unpack("<i", shp.read(4))[0]
        # The shapefile's bounding box (lower left, upper right)
        self.bbox = _Array('d', unpack("<4d", shp.read(32)))
        # Elevation
        self.elevation = _Array('d', unpack("<2d", shp.read(16)))
        # Measure
        self.measure = _Array('d', unpack("<2d", shp.read(16)))
#        self.fastreader=[]
#        if self.shapeType in (3,5,8,13,15,18,23,25,28,31):
#            self.fastreader.append(self.readbbox)

#    @staticmethod
#    def __readbbox(f, record):
#        record.bbox = _Array('d', unpack("<4d", f.read(32)))
#
#    @staticmethod
#    def __readint(f):
#        return unpack("<i", f.read(4))[0]
#
#    @staticmethod
#    def __readintarray(f, nParts):
#        return _Array('i', unpack("<%si" % nParts, f.read(nParts * 4)))
#
#    @staticmethod
#    def __readpoints(f, record, nPoints):
#        record.points = [_Array('d', unpack("<2d", f.read(16))) for p in range(nPoints)]
#
#    @staticmethod
#    def __readnpts(f):
#        return unpack("<i", f.read(4))[0]
#


    def __shape(self):
        """Returns the header info and geometry for a single shape."""
        f = self.__getFileObj(self.shp)
        record = _Shape()
        nParts = nPoints = zmin = zmax = mmin = mmax = None
        (recNum, recLength) = unpack(">2i", f.read(8))
        # Determine the start of the next record
        next_s = f.tell() + (2 * recLength)
        shapeType = unpack("<i", f.read(4))[0]
        record.shapeType = shapeType
#        print ('shape:lecture type ',shapeType)
        if shapeType != self.shapeType and shapeType != 0:
            print('erreur type_shape par rapport a l entete', self.shapeType,
                  shapeType)
        # For Null shapes create an empty points list for consistency
        if shapeType == 0:
            record.points = []
        # All shape types capable of having a bounding box
        elif shapeType in (3, 5, 8, 13, 15, 18, 23, 25, 28, 31):
            record.bbox = _Array('d', unpack("<4d", f.read(32)))
        # Shape types with parts
        if shapeType in (3, 5, 13, 15, 23, 25, 31):
            nParts = unpack("<i", f.read(4))[0]
        # Shape types with points
        if shapeType in (3, 5, 8, 13, 15, 23, 25, 31):
            nPoints = unpack("<i", f.read(4))[0]
        # Read parts
        if nParts:
            record.parts = _Array('i', unpack("<%si" % nParts, f.read(nParts * 4)))
        # Read part types for Multipatch - 31
        if shapeType == 31:
            record.partTypes = _Array('i', unpack("<%si" % nParts, f.read(nParts * 4)))
        # Read points - produces a list of [x,y] values
        if nPoints:
            record.points = [_Array('d', unpack("<2d", f.read(16))) for p in range(nPoints)]
        # Read z extremes and values
        if shapeType in (13, 15, 18, 31):
            (zmin, zmax) = unpack("<2d", f.read(16))
            record.z = _Array('d', unpack("<%sd" % nPoints, f.read(nPoints * 8)))
        # Read m extremes and values if header m values do not equal 0.0
        if shapeType in (13, 15, 18, 23, 25, 28, 31) and 0.0 not in self.measure:
            try:
                (mmin, mmax) = unpack("<2d", f.read(16))
                # Measure values less than -10e38 are nodata values according to the spec
                record.measure = []
                for measure in _Array('d', unpack("<%sd" % nPoints, f.read(nPoints * 8))):
                    if measure > -10e38:
                        record.measure.append(measure)
                    else:
                        record.measure.append(None)
            except:
                print('erreur shape lecture valeur M')
        # Read a single point
        if shapeType in (1, 11, 21):
            record.points = [_Array('d', unpack("<2d", f.read(16)))]
        # Read a single Z value
        if shapeType == 11:
            record.z = unpack("<d", f.read(8))
        # Read a single M value
        if shapeType in (11, 21):
            record.measure = unpack("<d", f.read(8))
        # Seek to the end of this record as defined by the record header because
        # the shapefile spec doesn't require the actual content to meet the header
        # definition.  Probably allowed for lazy feature deletion.
        f.seek(next_s)
        return record

    def __shape2(self):
        """Returns the header info and geometry for a single shape.
        version optimisee pour la vitesse"""
        f = self.__getFileObj(self.shp)
        record = _Shape()
        nParts = nPoints = zmin = zmax = mmin = mmax = None
        (recNum, recLength) = unpack(">2i", f.read(8))
        # Determine the start of the next record
        next_s = f.tell() + (2 * recLength)
        buff = f.read(2 * recLength)
        shapeType = unpack("<i", buff[0:4])[0]
        b = 4
        record.shapeType = shapeType
        # For Null shapes create an empty points list for consistency
        if shapeType == 0:
            record.points = []
        # All shape types capable of having a bounding box
        elif shapeType in (3, 5, 8, 13, 15, 18, 23, 25, 28, 31):
            record.bbox = _Array('d', unpack("<4d", buff[b:b+32]))
            b = b+32
        # Shape types with parts
        if shapeType in (3, 5, 13, 15, 23, 25, 31):
            nParts = unpack("<i", buff[b:b+4])[0]
            b = b+4
        # Shape types with points
        if shapeType in (3, 5, 8, 13, 15, 23, 25, 31):
            nPoints = unpack("<i", buff[b:b+4])[0]
            b = b+4
        # Read parts
        if nParts:
            record.parts = _Array('i', unpack("<%si" % nParts, buff[b:b+nParts * 4]))
            b = b+nParts * 4
        # Read part types for Multipatch - 31
        if shapeType == 31:
            record.partTypes = _Array('i', unpack("<%si" % nParts, buff[b:b+nParts * 4]))
            b = b+nParts*4
        # Read points - produces a list of [x,y] values
        if nPoints:
            record.points = [_Array('d', unpack("<2d", buff[b+16*p:b+16*p+16]))
                             for p in range(nPoints)]
            b = b+nPoints*16
        # Read z extremes and values
        if shapeType in (13, 15, 18, 31):
            (zmin, zmax) = unpack("<2d", buff[b:b+16])
            b = b+16
            record.z = _Array('d', unpack("<%sd" % nPoints, buff[b:b+nPoints * 8]))
            b = b+nPoints*8
        # Read m extremes and values if header m values do not equal 0.0
        if shapeType in (13, 15, 18, 23, 25, 28, 31) and 0.0 not in self.measure:
            (mmin, mmax) = unpack("<2d", buff[b:b+16])
            b = b+16
            # Measure values less than -10e38 are nodata values according to the spec
            record.m = []
            for m in _Array('d', unpack("<%sd" % nPoints, buff[b:b+nPoints * 8])):
                if m > -10e38:
                    record.m.append(m)
                else:
                    record.m.append(None)
            b = b+nPoints*8
        # Read a single point
        if shapeType in (1, 11, 21):
            record.points = [_Array('d', unpack("<2d", buff[b:b+16]))]
            b = b+16
        # Read a single Z value
        if shapeType == 11:
            record.z = unpack("<d", buff[b:b+8])
            b = b+8
        # Read a single M value
        if shapeType in (11, 21):
            record.m = unpack("<d", buff[b:b+8])
            b = b+8
        # Seek to the end of this record as defined by the record header because
        # the shapefile spec doesn't require the actual content to meet the header
        # definition.  Probably allowed for lazy feature deletion.
        f.seek(next_s)
        return record


    def __shapeIndex(self, i=None):
        """Returns the offset in a .shp file for a shape based on information
        in the .shx index file."""
        shx = self.shx
        if not shx:
            return None
        if not self._offsets:
            # File length (16-bit word * 2 = bytes) - header length
            shx.seek(24)
            shxRecordLength = (unpack(">i", shx.read(4))[0] * 2) - 100
            numRecords = shxRecordLength // 8
            # Jump to the first record.
            shx.seek(100)
            for r in range(numRecords):
                # Offsets are 16-bit words just like the file length
                self._offsets.append(unpack(">i", shx.read(4))[0] * 2)
                shx.seek(shx.tell() + 4)
        if not i == None:
            return self._offsets[i]

    def shape(self, i=0):
        """Returns a shape object for a shape in the the geometry
        record file."""
        shp = self.__getFileObj(self.shp)
        i = self.__restrictIndex(i)
        offset = self.__shapeIndex(i)
        if not offset:
            # Shx index not available so iterate the full list.
            for j, k in enumerate(self.iterShapes()):
                if j == i:
                    return k
        shp.seek(offset)
        return self.__shape()

    def shapes(self):
        """Returns all shapes in a shapefile."""
        shp = self.__getFileObj(self.shp)
        # Found shapefiles which report incorrect
        # shp file length in the header. Can't trust
        # that so we seek to the end of the file
        # and figure it out.
        shp.seek(0, 2)
        self.shpLength = shp.tell()
        shp.seek(100)
        shapes = []
        while shp.tell() < self.shpLength:
            shapes.append(self.__shape())
        return shapes

    def iterShapes(self):
        """Serves up shapes in a shapefile as an iterator. Useful
        for handling large shapefiles."""
        shp = self.__getFileObj(self.shp)
        shp.seek(0, 2)
        self.shpLength = shp.tell()
        shp.seek(100)
        while shp.tell() < self.shpLength:
            yield self.__shape()

    def __dbfHeaderLength(self):
        """Retrieves the header length of a dbf file header."""
        if not self.__dbfHdrLength:
            if not self.dbf:
                raise ShapefileException("Shapefile Reader requires a shapefile\
                                         or file-like object. (no dbf file found)")
            dbf = self.dbf
            (self.numRecords, self.__dbfHdrLength) = \
                    unpack("<xxxxLH22x", dbf.read(32))
            #print("shapefile : taille entete dbf",self.__dbfHdrLength)
        return self.__dbfHdrLength

    def __dbfHeader(self):
        """Reads a dbf header. Xbase-related code borrows heavily from ActiveState
        Python Cookbook Recipe 362715 by Raymond Hettinger"""
        if not self.dbf:
            raise ShapefileException("Shapefile Reader requires a shapefile\
                                     or file-like object. (no dbf file found)")
        dbf = self.dbf
        headerLength = self.__dbfHeaderLength()
        numFields = (headerLength - 33) // 32
        for field in range(numFields):
            fieldDesc = list(unpack("<11sc4xBB14x", dbf.read(32)))
            name = 0
            idx = 0
            if b("\x00") in fieldDesc[name]:
                idx = fieldDesc[name].index(b("\x00"))
            else:
                idx = len(fieldDesc[name]) - 1
            fieldDesc[name] = fieldDesc[name][:idx]
            fieldDesc[name] = u(fieldDesc[name])
            fieldDesc[name] = fieldDesc[name].lstrip()
            fieldDesc[1] = u(fieldDesc[1])
            self.fields.append(fieldDesc)
        terminator = dbf.read(1)
        if terminator != b("\r"):
            raise ShapefileException("Shapefile dbf header lacks expected\
                                     terminator. (likely corrupt?)")
        self.fields.insert(0, ('DeletionFlag', 'C', 1, 0))

    def __recordFmt(self):
        """Calculates the size of a .shp geometry record."""
        if not self.numRecords:
            self.__dbfHeader()
        fmt = ''.join(['%ds' % fieldinfo[2] for fieldinfo in self.fields])
        fmtSize = calcsize(fmt)
        self.recFmt = (fmt, fmtSize)
        return (fmt, fmtSize)

    def __record(self):
        """Reads and returns a dbf record row as a list of values."""
        f = self.__getFileObj(self.dbf)

        recFmt = self.recFmt if self.recFmt else self.__recordFmt()
        recordContents = unpack(recFmt[0], f.read(recFmt[1]))
        if recordContents[0] != b(' '):
            # deleted record
            return None
        record = []
        for (name, typ, size, deci), value in zip(self.fields, recordContents):
            if name == 'DeletionFlag':
                continue
#            elif not value.strip():
 #               record.append(value.strip())
#                continue
            elif typ == "N":
                value = value.replace(b('\0'), b('')).strip()
                value = value.replace(b('*'), b(''))  # QGIS NULL is all '*' chars
                try:
                    if value == b(''):
                        value = None
                    elif deci:
                        value = float(value)
                    else:
                        value = int(value)
                except:
                    pass
            elif typ == b('D'):
                if value.count(b('0')) == len(value):  # QGIS NULL is all '0' chars
                    value = None
                else:
                    try:
                        y, m, d = int(value[:4]), int(value[4:6]), int(value[6:8])
                        # modifie pour retourner la date en texte
                        value = '/'.join([y, m, d])
                    except:
                        value = value.strip()
            elif typ == b('L'):
                value = (value in b('YyTt') and b('T')) or \
                                        (value in b('NnFf') and b('F')) or b('?')
            else:
                value = u(value)
                value = value.strip()
            record.append(value)
        return record

    def record(self, i=0):
        """Returns a specific dbf record based on the supplied index."""
        fich = self.__getFileObj(self.dbf)
        if not self.numRecords:
            self.__dbfHeader()
        i = self.__restrictIndex(i)
        recSize = self.__recordFmt()[1]
        fich.seek(0)
        fich.seek(self.__dbfHeaderLength() + (i * recSize))
        return self.__record()

    def records(self):
        """Returns all records in a dbf file."""
        if not self.numRecords:
            self.__dbfHeader()
        records = []
        fich = self.__getFileObj(self.dbf)
        fich.seek(self.__dbfHeaderLength())
        for i in range(self.numRecords):
            r = self.__record()
            if r:
                records.append(r)
        return records

    def iterRecords(self):
        """Serves up records in a dbf file as an iterator.
        Useful for large shapefiles or dbf files."""
        if not self.numRecords:
            self.__dbfHeader()
        fich = self.__getFileObj(self.dbf)
        fich.seek(self.__dbfHeaderLength())
        for i in range(self.numRecords):
            r = self.__record()
            if r:
                yield r

    def shapeRecord(self, i=0):
        """Returns a combination geometry and attribute record for the
        supplied record index."""
        i = self.__restrictIndex(i)
        return _ShapeRecord(shape=self.shape(i), record=self.record(i))

    def shapeRecords(self):
        """Returns a list of combination geometry/attribute records for
        all records in a shapefile."""
        #shapeRecords = []
        return [_ShapeRecord(shape=rec[0], record=rec[1]) \
                                for rec in zip(self.shapes(), self.records())]

    def iterShapeRecords(self):
        """Returns a generator of combination geometry/attribute records for
        all records in a shapefile."""
        for shape, record in zip(self.iterShapes(), self.iterRecords()):
            yield _ShapeRecord(shape=shape, record=record)


class streamWriter:
    '''ecriture de shapefiles au fil de l'eau'''
    box = {0:(0, 0, 0), 1:(0, 0, 0), 3:(1, 0, 0), 5:(1, 0, 0), 8:(1, 0, 0),
           11:(0, 0, 0), 13:(1, 1, 0), 15:(1, 1, 0), 18:(1, 1, 0), 23:(1, 0, 1),
           25:(1, 0, 1), 28:(1, 0, 1), 31:(1, 0, 1)}
    sizelist = {0:(0, 0, 0), 1:(16, 0, 0), 3:(40, 4, 16), 5:(40, 4, 16),
                8:(36, 0, 16), 11:(32, 0, 0), 13:(56, 4, 24), 15:(56, 4, 24),
                18:(52, 0, 24), 21:(24, 0, 0), 23:(56, 4, 24), 25:(56, 4, 24),
                28:(36, 0, 24), 31:(72, 8, 32)}

    def __init__(self, shapeType=None, mode='base', fich='defaut'):

        self.shapeType = shapeType
        self.filename = os.path.splitext(fich)[0]
        self.name = fich
        self.shp = None
        self.shx = None
        self.dbf = None
        self.shapesize = 0 # accumulation of size
        self.recNum = 1
        self.fields = []
        self.xmin, self.xmax, self.ymin, self.ymax = 0.0, 0.0, 0.0, 0.0
        self.zmin, self.zmax, self.mmin, self.mmax = 0.0, 0.0, 0.0, 0.0
        self.cumul_taille = 0

    def __getFileObj(self, fich):
        """Safety handler to verify file-like objects"""
        if not fich:
            raise ShapefileException("No file-like object available.")
        elif hasattr(fich, "write"):
            return fich
        else:
            pth = os.path.split(fich)[0]
            if pth and not os.path.exists(pth):
                os.makedirs(pth)
            return open(fich, "wb")

    def close(self):
        ''' ferme le fichier'''
#        print("dans close ",self.filename)
        self.__shapefileHeader(headerType='shp')
        self.shp.close()
        self.shp = None

        self.__shapefileHeader(headerType='shx')
        self.shx.close()
        self.shx = None
        self.__dbfHeader()

        self.dbf.close()
        self.dbf = None
    def reopen(self):
        '''reouvre le fichier'''
        print("dans reopen()", self.filename)
        nomshp = self.filename+'.shp'
        self.shp = open(nomshp, 'ab')
        nomshx = self.filename+'.shx'
        self.shx = open(nomshx, 'ab')
        nomdbf = self.filename+'.dbf'
        self.dbf = open(nomdbf, 'ab')
    def open(self):
        '''ouvre les fichier'''
#        print ('dans open',self.filename)
        nomshp = self.filename+'.shp'
        self.shp = self.__getFileObj(nomshp)
        self.shp.seek(100)
        nomshx = self.filename+'.shx'
        self.shx = self.__getFileObj(nomshx)
        self.shx.seek(100)
        nomdbf = self.filename+'.dbf'
        self.dbf = self.__getFileObj(nomdbf)
        self.__dbfHeader()

    def finalise(self):
        '''plus d'utilisation du fichier '''
        self.shp.close()
        self.shx.close()
        self.dbf.close()
        return

    def __shapeLength(self, s):
        '''calculate the length of one shape'''

        nParts = len(s.parts) if hasattr(s, 'parts') else 0

        nPoints = len(s.points) if hasattr(s, 'points') else 0

        lf, lpart, lpt = self.sizelist[self.shapeType]
        size = 12+lf+lpart*nParts+lpt*nPoints

        return size

    def __shapefileHeader(self, headerType='shp'):
        """Writes the specified header type to the specified file-like object.
        Several of the shapefile formats are so similar that a single generic
        method to read or write them is warranted."""
        f = self.shp if headerType == 'shp' else self.shx
        f.seek(0)
        # File code, Unused bytes
        f.write(pack(">6i", 9994, 0, 0, 0, 0, 0))
        # File length (Bytes / 2 = 16-bit words)
#        print('ecriture entete shp/shx',self.cumul_taille,self.recNum-1,headerType)
        if headerType == 'shp':
            f.write(pack(">i", self.cumul_taille))
#            print ("taille shape", hex(self.cumul_taille))
        else:
            f.write(pack('>i', ((100 + ((self.recNum-1) * 8)) // 2)))
        f.write(pack("<2i", 1000, self.shapeType))
        # The shapefile's bounding box (lower left, upper right)
#        print ("shapebbox",self.xmin,self.ymin,self.xmax,self.ymax)
        if self.shapeType != 0:
            f.write(pack("<4d", self.xmin, self.ymin, self.xmax, self.ymax))
        else:
            f.write(pack("<4d", 0, 0, 0, 0))
        if self.zmin is None:
            self.zmin, self.zmax = 0, 0
        if self.mmin is None:
            self.mmin, self.mmax = 0, 0
        f.write(pack("<4d", self.zmin, self.zmax, self.mmin, self.mmax))


    def __dbfHeader(self):
        """Writes the dbf header and field descriptors."""
        f = self.dbf
        f.seek(0)
        version = 3
        year, month, day = time.localtime()[:3]
        year -= 1900
        # Remove deletion flag placeholder from fields

        numRecs = self.recNum
        numFields = len(self.fields)
        headerLength = numFields * 32 + 33
        recordLength = sum([int(field[2]) for field in self.fields]) + 1
        header = pack('<BBBBLHH20x', version, year, month, day, numRecs,
                      headerLength, recordLength)
        f.write(header)
#        print ('entete shape version, year, month, day, numRecs,headerLength, recordLength',
#               version, year, month, day, numRecs,headerLength, recordLength)
        # Field descriptors
        for field in self.fields:
            name, fieldType, size, decimal = field
#            print (self.name,"creation champs ", name, fieldType, size, decimal)
            name = b(name.upper())
            name = name.replace(b(' '), b('_'))
            name = name.ljust(11).replace(b(' '), b('\x00'))
            fieldType = b(fieldType)
            size = int(size)
            decimal = int(decimal)
            fld = pack('<11sc4xBB14x', name, fieldType, size, decimal)
#            print ('champs name, fieldType, size, decimal',name, fieldType, size, decimal)
            f.write(fld)
        # Terminator
        f.write(b('\r'))



    def __writeshape(self, s):
        ''' writes one shape'''
        # Record number, Content length place holder
        f = self.shp
        offset = f.tell()
        lrec = self.__shapeLength(s)//2
        self.shapesize += lrec
        self.shp.write(pack(">2i", self.recNum, lrec-4))
        self.recNum += 1
        #recNum=self.recNum
        start = f.tell()
        # Shape Type
        if self.shapeType != 31:
            s.shapeType = self.shapeType
        f.write(pack("<i", s.shapeType))
        # All shape types capable of having a bounding box
        lf, np, npt = self.sizelist[self.shapeType]# Shape types with parts
        bb, zb, mb = self.box[self.shapeType]
        box = self.__bbox(s)
        if bb:
            f.write(pack("<4d", *box))

        if np:
            # Number of parts
            f.write(pack("<i", len(s.parts)))
        # Shape types with multiple points per record
        if npt:
            # Number of points
            f.write(pack("<i", len(s.points)))
            if s.shapeType == 31:
                for pt in s.partTypes:
                    f.write(pack("<i", pt))
                [f.write(pack("<2d", *p[:2])) for p in s.points]
        elif self.shapeType != 0:
            f.write(pack("<2d", s.points[0][0], s.points[0][1]))
#            print ("ecriture pints ",np,npt,s.points[0])
            if self.shapeType == 11:
                f.write(pack("<d", s.points[0][2]))
            if self.shapeType == 21:
                f.write(pack("<d", s.points[0][3]))

        # Write part indexes
        if zb:
            f.write(pack("<2d", *self.__zbox(s)))
            [f.write(pack("<d", p[2])) for p in s.points]
        if mb:
            f.write(pack("<2d", *self.__mbox(s)))
            [f.write(pack("<d", p[3])) for p in s.points]


        finish = f.tell()
        length = (finish - start) // 2
        self.cumul_taille += length
        f2 = self.shx
        f2.write(pack(">i", offset // 2))
        f2.write(pack(">i", length))


#    def __dbfrecord(self,record):
#
#        for (fieldName, fieldType, size, dec), value in zip(self.fields, record):
#            fieldType = fieldType.upper()
#            size = int(size)
#            if fieldType.upper() == "N":
#                value = str(value).rjust(size)
#            elif fieldType == 'L':
#                value = str(value)[0].upper()
#            else:
#                value = str(value)[:size].ljust(size)
#            if len(value) != size:
#                raise ShapefileException(
#                    "Shapefile Writer unable to pack incorrect sized value"
#                    " (size %d) into field '%s' (size %d)." % (len(value), fieldName, size))
#            value = b(value)
#            self.dbf.write(value)
#            print ('ecriture dbf ',value)

    def null(self):
        """Creates a null shape."""
        shape = _Shape(self.shapeType)
        self.__writeshape(shape)

    def point(self, coord_x, coord_y, coord_z=0, mes=0):
        """Creates a point shape."""
        pointShape = _Shape(self.shapeType)
        pointShape.points.append([coord_x, coord_y, coord_z, mes])
        self.__writeshape(pointShape)

    def poly(self, parts=[], shapeType=POLYGON, partTypes=[]):
        """Creates a shape that has multiple collections of points (parts)
        including lines, polygons, and even multipoint shapes. If no shape type
        is specified it defaults to 'polygon'. If no part types are specified
        (which they normally won't be) then all parts default to the shape type.
        """
        polyShape = _Shape(shapeType)
        polyShape.parts = []
        polyShape.points = []
        # Make sure polygons are closed
        if shapeType in (5, 15, 25, 31):
            for part in parts:
                if part[0] != part[-1]:
                    part.append(part[0])
        for part in parts:
            polyShape.parts.append(len(polyShape.points))
            for point in part:
                # Ensure point is list
                if not isinstance(point, list):
                    point = list(point)
                # Make sure point has z and m values
                while len(point) < 4:
                    point.append(0)
                polyShape.points.append(point)
        if polyShape.shapeType == 31:
            if not partTypes:
                for part in parts:
                    partTypes.append(polyShape.shapeType)
            polyShape.partTypes = partTypes
        self.__writeshape(polyShape)

    def field(self, name, fieldType="", size="50", decimal=0):
        """Adds a dbf field descriptor to the shapefile."""
#        print ("dans fied",name, fieldType, size, decimal)
        if fieldType in ('TEXTE', 'T', 'C', 'texte', 'text'):
            fieldType = 'C'
            defsize = 50
            defdec = 0
        elif fieldType in ('REEL', 'F', 'double precision', 'float', 'L'):
            fieldType = 'N'
            defsize = 18
            defdec = 3
        elif fieldType in ('INT', 'I', 'E', 'N', 'entier', 'integer'):
            fieldType = 'N'
            defsize = 8
            defdec = 0
        elif fieldType in ('EL', 'E', 'N', 'bigint'):
            fieldType = 'N'
            defsize = 16
            defdec = 0
        elif fieldType in ('DATE', 'D', 'date', 'timestamp without time zone'):
            fieldType = 'D'
            defsize = 16
            defdec = 0
        else:
            print('type inconnu', name, '->', fieldType, '<-')
            print('objet:', self.fields)
            raise TypeError
            fieldType = 'C'
            defsize = 80
            defdec = 0
        size = int(size)
        if size > 255:
            size = 255
        decimal = int(decimal)
        if size == 0:
            size = defsize
            decimal = defdec
        self.fields.append((name, fieldType, size, decimal))

    def record(self, **recordDict):
        """Creates a dbf attribute record. You can submit either a sequence of
        field values or keyword arguments of field names and values. Before
        adding records you must add fields for the record values using the
        fields() method. If the record values exceed the number of fields the
        extra ones won't be added. In the case of using keyword arguments to specify
        field/value pairs only fields matching the already registered fields
        will be added."""
        #fieldCount = len(self.fields)
        # Compensate for deletion flag

        for (fieldName, fieldType, size, dec) in self.fields:
            value = recordDict.get(fieldName, '')
#            print('shp ecriture champ ',fieldName,fieldType,size, dec,
#                  value.encode('ascii','ignore').decode('ascii'))

            size = int(size)
            if fieldType.upper() == "N":
                value = str(value).rjust(size)
                if len(value) > size:
                    value = str(round(float(value), dec)).rjust(size)
            elif fieldType == 'L':
                value = str(value)[0].upper()
            else:
                value = str(value)[:size].ljust(size)
            if len(value) != size:
                raise ShapefileException(
                    "Shapefile Writer unable to pack incorrect sized value"
                    " (size %d) into field '%s' (size %d). %s" %
                    (len(value), fieldName, size, value))
            value = b(value)
            self.dbf.write(value)
        self.dbf.write(b('\r'))
#            print ('ecriture dbf ',fieldName,value)


    def __bbox(self, shape):
        if shape.points:
            val_x, val_y = list(zip(*shape.points))[:2]
        else:
            val_x, val_y = [0], [0]
        xmin, ymin, xmax, ymax = min(val_x), min(val_y), max(val_x), max(val_y)
        self.xmin = min(xmin, self.xmin) if self.xmin else xmin
        self.ymin = min(ymin, self.ymin) if self.ymin else ymin
        self.xmax = max(xmax, self.xmax) if self.xmax else xmax
        self.ymax = max(ymax, self.ymax) if self.ymax else ymax
        return [xmin, ymin, xmax, ymax]

    def __zbox(self, shape):
        try:
            val_z = [point[2] for point in shape.points]
        except IndexError:
            pass
        if not val_z:
            val_z.append(0)
        zmin, zmax = min(val_z), max(val_z)
        self.zmin = min(zmin, self.zmin) if self.zmin else zmin
        self.zmax = max(zmax, self.zmax) if self.zmax else zmax
        return [zmin, zmax]


    def __mbox(self, shape):
        '''mimites des attributs m '''
        try:
            mes = [point[3] for point in shape.points]
        except IndexError:
            pass
        if not mes:
            mes.append(0)
        mmin, mmax = min(mes), max(mes)
        self.mmin = min(mmin, self.mmin) if self.mmin else mmin
        self.zmax = max(mmax, self.mmax) if self.mmax else mmax
        return [mmin, mmax]





# Begin Testing
def test():
    '''test module '''
    import doctest
    doctest.NORMALIZE_WHITESPACE = 1
    doctest.testfile("README.txt", verbose=1)

if __name__ == "__main__":
    """
    Doctests are contained in the file 'README.txt'. This library was originally developed
    using Python 2.3. Python 2.4 and above have some excellent improvements in the built-in
    testing libraries but for now unit testing is done using what's available in
    2.3.
    """
    test()
