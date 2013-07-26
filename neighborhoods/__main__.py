#!/usr/bin/python

import argparse
import configparser
import os.path
import sqlite3
from neighborhoods.importer.cbs_importer import CBSImporter

current_dir = os.path.dirname(os.path.abspath(__file__)) + "/"

def _open_database_connection(config):
    global database_path, database_exists, connection
    database_path = config['database']['path']
    database_exists = os.path.isfile(database_path)
    connection = sqlite3.connect(database_path)
    if not database_exists:
        connection.cursor().executescript(open(current_dir + "database.sqlite.sql").read())
        connection.commit()
    return connection

def main():
    def create_root_parser():
        root_parser = argparse.ArgumentParser(
            prog="neighborhoods",
            description="A program for creating various geographic area representations.")
        subparsers = root_parser.add_subparsers(dest="action")
        create_import_parser(subparsers)
        return root_parser

    def create_import_parser(subparsers):
        description = "Import geographic data into the Neighborhoods' database."
        import_parser = subparsers.add_parser("import",
            description=description,
            help=description)
        import_parser.add_argument("source",
            metavar="source",
            type=str,
            help="The source of the geographic data. Either a zip file or a directory.")
    def parse_import_parser(args, connection):
        path = args.source
        importer = CBSImporter(connection)
        if os.path.isdir(path):
            print("Importing from directory {}...".format(path))
            importer.import_from_directory(path, connection)
        elif os.path.isfile(path) and os.path.splitext(path)[1] == ".zip":
            print("Importing from zip file {}...".format(path))
            importer.import_from_zipfile(path, connection)
        else:
            print("Unknown source {}.".format(path))
            exit(2)
        connection.cursor().execute("VACUUM;")
        print("Import completed successfully.")

    config = configparser.ConfigParser()
    config.read(current_dir + "config.ini")

    root_parser = create_root_parser()
    args = root_parser.parse_args()

    connection = _open_database_connection(config)

    if args.action == "import":
        parse_import_parser(args, connection)

if __name__ == "__main__":
    main()