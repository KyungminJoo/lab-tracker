import os, pathlib
basedir = pathlib.Path(__file__).resolve().parent

class Config:
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + str(basedir / "../data/labtracker.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    WATCH_PATH = os.getenv(
        "WATCH_PATH",
        "/volume1/3shape_orders/3Shape Dental System Orders",
    )
    PRINTER_NAME = os.getenv("PRINTER_NAME", "Label")
    SITE_URL = os.getenv("SITE_URL", "http://localhost:15000")
