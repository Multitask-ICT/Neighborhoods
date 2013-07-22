CREATE TABLE Coordinate (
    CoordinateId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Geocode_Latitude REAL NOT NULL,
    Geocode_Longitude REAL NOT NULL,
    RD_X REAL NOT NULL,
    RD_Y REAL NOT NULL,

    UNIQUE (Geocode_Latitude, Geocode_Longitude),
    UNIQUE (RD_X, RD_Y)
);


CREATE TABLE AreaType (
    AreaTypeId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    AreaType TEXT NOT NULL,

    UNIQUE (AreaType)
);


CREATE TABLE Area (
    AreaId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Code TEXT NOT NULL,
    AreaTypeId INTEGER NOT NULL,
    ParentAreaId INTEGER NULL,

    FOREIGN KEY (AreaTypeId) REFERENCES AreaType (AreaTypeId),
    FOREIGN KEY (ParentAreaId) REFERENCES Area (AreaId),

    UNIQUE (Code)
);
CREATE INDEX Area_AreaTypeId ON Area (AreaTypeId);


CREATE TABLE Shape (
    ShapeId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    AreaId INTEGER NOT NULL,

    FOREIGN KEY (AreaId) REFERENCES Area (AreaId)
);
CREATE INDEX Shape_AreaId ON Shape (AreaId);


CREATE TABLE ShapeCoordinate (
    ShapeCoordinateId INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    ShapeId INTEGER NOT NULL,
    CoordinateId INTEGER NOT NULL,
    Ordering INTEGER NOT NULL,

    FOREIGN KEY (ShapeId) REFERENCES Shape (ShapeId),
    FOREIGN KEY (CoordinateId) REFERENCES Coordinate (CoordinateId),

    UNIQUE (ShapeId, CoordinateId, Ordering)
);
