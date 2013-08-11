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

    def import_area(self, shapefile_reader, area_type, has_parent):
        cursor = self._connection.cursor()
        area_type_id = self._attach_area_type(area_type, cursor)

        for record, shape in zip(shapefile_reader.iterRecords(), shapefile_reader.iterShapes()):
            code, name = record[0].strip(), record[1].strip()
            parent_code = record[3].strip() if has_parent else None

            if len(name) == 0 or self._area_exists(code, cursor):
                continue

            area_id = self._insert_area(name, code, area_type_id, parent_code, cursor)

            for shape in self._split_detached_shapes(shape.points):
                self._insert_shape(area_id, shape, cursor)

        self._connection.commit()

    def _attach_area_type(self, area_type, cursor):
        cursor.execute("SELECT area_type_id FROM area_type WHERE area_type = ?", (area_type,))
        area_type_id = cursor.fetchone()
        if area_type_id is not None:
            return area_type_id[0]
        else:
            cursor.execute("INSERT INTO area_type (area_type) VALUES (?)", (area_type,))
            return cursor.lastrowid

    def _area_exists(self, area_code, cursor):
        cursor.execute("SELECT EXISTS(SELECT code FROM area WHERE code = ?)", (area_code,))
        return cursor.fetchone()[0] > 0

    def _insert_area(self, name, code, area_type_id, parent_code, cursor):
        cursor.execute(
            "INSERT INTO area (name, code, area_type_id, parent_area_id) "
            "SELECT ?, ?, ?, (SELECT area_id FROM area WHERE code = ?)",
            (name, code, area_type_id, parent_code)
        )
        return cursor.lastrowid

    def _split_detached_shapes(self, points):
        if not any(points):
            return []
        elif points[0] == points[-1]:
            return [points]
        else:
            shape_endpoint = points.index(points[0], 1)
            return [points[:shape_endpoint + 1]] + self._split_detached_shapes(points[shape_endpoint + 1:])

    def _insert_shape(self, area_id, points, cursor):
        cursor.execute(
            "INSERT INTO shape (area_id) VALUES (?)",
            (area_id,)
        )
        shape_id = cursor.lastrowid

        self._insert_coordinates(shape_id, points, cursor)

    def _insert_coordinates(self, shape_id, points, cursor):
        convert_to_geocode_visitor = ConvertToGeocodeVisitor()
        for point_index in range(len(points)):
            rd_coordinate = RD(*points[point_index])
            geocode_coordinate = convert_to_geocode_visitor.visit_rd(rd_coordinate)

            coordinate_id = self._attach_coordinate(geocode_coordinate, rd_coordinate, cursor)

            cursor.execute(
                "INSERT INTO shape_coordinate (shape_id, coordinate_id, ordering) "
                "SELECT ?, ?, ?",
                (shape_id, coordinate_id, point_index)
            )

    def _attach_coordinate(self, geocode_coordinate, rd_coordinate, cursor):
        cursor.execute(
            "SELECT coordinate_id FROM coordinate "
            "WHERE (geocode_latitude = ? AND geocode_longitude = ?) "
            "OR    (rd_x = ? AND rd_y = ?) "
            "LIMIT 1",
            tuple(geocode_coordinate) + tuple(rd_coordinate)
        )
        coordinate_id = cursor.fetchone()
        if coordinate_id is not None:
            return coordinate_id[0]
        else:
            cursor.execute(
                "INSERT INTO coordinate (geocode_latitude, geocode_longitude, rd_x, rd_y) "
                "VALUES (?, ?, ?, ?)",
                tuple(geocode_coordinate) + tuple(rd_coordinate)
            )
            return cursor.lastrowid
