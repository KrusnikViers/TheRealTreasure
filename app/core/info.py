import os
import pathlib


# RELEASE-UPDATE
APP_DIR = pathlib.Path(os.path.realpath(__file__)).parent.parent
ROOT_DIR = APP_DIR.parent
DEFAULT_DB_PATH = '/instance/storage'
PROJECT_NAME = 'TheRealTreasure'
PROJECT_VERSION = '1.0.0'
PROJECT_FULL_NAME = '{} v{}'.format(PROJECT_NAME, PROJECT_VERSION)
