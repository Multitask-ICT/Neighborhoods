CREATE TABLE coordinate (
    coordinate_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    geocode_latitude REAL NOT NULL,
    geocode_longitude REAL NOT NULL,
    rd_x REAL NOT NULL,
    rd_y REAL NOT NULL,

    UNIQUE (geocode_latitude, geocode_longitude),
    UNIQUE (rd_x, rd_y)
);


CREATE TABLE area_type (
    area_type_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    area_type TEXT NOT NULL,

    UNIQUE (area_type)
);


CREATE TABLE area (
    area_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    area_type_id INTEGER NOT NULL,
    parent_area_id INTEGER NULL,
    FOREIGN KEY (area_type_id) REFERENCES area_type (area_type_id),
    FOREIGN KEY (parent_area_id) REFERENCES area (area_id),

    UNIQUE (code)
);
CREATE INDEX area__area_type_id ON area (area_type_id);


CREATE TABLE shape (
    shape_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    area_id INTEGER NOT NULL,

    FOREIGN KEY (area_id) REFERENCES area (area_id)
);
CREATE INDEX shape__area_id ON shape (area_id);


CREATE TABLE shape_coordinate (
    shape_coordinate_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    shape_id INTEGER NOT NULL,
    coordinate_id INTEGER NOT NULL,
    ordering INTEGER NOT NULL,

    FOREIGN KEY (shape_id) REFERENCES shape (shape_id),
    FOREIGN KEY (coordinate_id) REFERENCES coordinate (coordinate_id),

    UNIQUE (shape_id, coordinate_id, ordering)
);
