import os


class paths:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    RES_DIR = os.path.join(BASE_DIR, 'res')
