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
    LABEL_OUTPUT_DIR = os.getenv("LABEL_OUTPUT_DIR")
    try:
        LABEL_WIDTH_PX = int(os.getenv("LABEL_WIDTH_PX", "400"))
    except ValueError:
        LABEL_WIDTH_PX = 400

    try:
        LABEL_HEIGHT_PX = int(os.getenv("LABEL_HEIGHT_PX", "180"))
    except ValueError:
        LABEL_HEIGHT_PX = 180
