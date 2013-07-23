import shutil
import tempfile
from zipfile import ZipFile
from geographic_coordinates.convert.convert_to_geocode_visitor import ConvertToGeocodeVisitor
from geographic_coordinates.rd import RD
import shapefile


class CBSImporter():
    @classmethod
    def import_from_zipfile(cls, path_to_zip, connection):
        tempdir = tempfile.mkdtemp()
        zipfile = ZipFile(path_to_zip)
        zipfile.extractall(tempdir)

        try:
            cls.import_from_directory(tempdir, connection)
        except:
            raise
        finally:
            shutil.rmtree(tempdir)

    @classmethod
    def import_from_directory(cls, directory_path, connection):
        importer = cls(connection)
        importer.import_area(shapefile.Reader("{}/gem_2012_v1".format(directory_path)), "gemeente", False)
        importer.import_area(shapefile.Reader("{}/wijk_2012_v1".format(directory_path)), "wijk", True)
        importer.import_area(shapefile.Reader("{}/buurt_2012_v1".format(directory_path)), "buurt", True)


    def __init__(self, connection):
        self._connection = connection

    def import_area(self, shape_reader, area_type, has_parent):
        cursor = self._connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO AreaType (AreaType) VALUES (?)", (area_type,))

        for record, shape in zip(shape_reader.iterRecords(), shape_reader.iterShapes()):
            code, name = record[0].strip(), record[1].strip()
            parent_code = record[3].strip() if has_parent else None

            if len(name) == 0:
                continue

            cursor.execute("SELECT EXISTS(SELECT Code FROM Area WHERE Code = ?)", (code,))
            if cursor.fetchone()[0] > 0:
                continue

            cursor.execute(
                "INSERT INTO Area (Name, Code, AreaTypeId, ParentAreaId) "
                "SELECT ?, ?, (SELECT AreaTypeId FROM AreaType WHERE AreaType = ?), (SELECT AreaId FROM Area WHERE Code = ?)",
                (name, code, area_type, parent_code)
            )
            area_id = cursor.lastrowid

            cursor.execute(
                "INSERT INTO Shape (AreaId) VALUES (?)",
                (area_id,)
            )
            shape_id = cursor.lastrowid

            convert_to_geocode_visitor = ConvertToGeocodeVisitor()
            for point_index in range(len(shape.points)):
                rd_coordinate = RD(*shape.points[point_index])
                geocode_coordinate = convert_to_geocode_visitor.visit_rd(rd_coordinate)
                cursor.execute(
                    "INSERT OR IGNORE INTO Coordinate (Geocode_Latitude, Geocode_Longitude, RD_X, RD_Y) VALUES (?, ?, ?, ?)",
                    tuple(geocode_coordinate) + tuple(rd_coordinate)
                )

                cursor.execute(
                    "INSERT INTO ShapeCoordinate (ShapeId, CoordinateId, Ordering) "
                    "SELECT ?, (SELECT CoordinateId FROM Coordinate WHERE (Geocode_Latitude = ? AND Geocode_Longitude = ?) OR (RD_X = ? AND RD_Y = ?) LIMIT 1), ?",
                    (shape_id, geocode_coordinate.latitude, geocode_coordinate.longitude, rd_coordinate.x, rd_coordinate.y, point_index)
                )

        self._connection.commit()
