from setuptools import setup, find_packages

setup(
    name="Neighborhoods",
    author="Jesse van Assen",
    description="A tool to represent geographic neighborhood data in various formats.",
    packages=find_packages(),
    package_data={
        "neighborhoods":[
            "database.sqlite.sql",
            "config.ini"
        ]
    },
    requires=[
        "geographic_coordinates",
        "pyshp"
    ]
)