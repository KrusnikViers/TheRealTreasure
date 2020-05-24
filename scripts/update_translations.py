from app.core.info import APP_DIR
from app.core.utils import global_logging_init
from app.i18n.updater import TranslationsUpdater

global_logging_init()

updater = TranslationsUpdater(APP_DIR.joinpath('i18n'), APP_DIR)
updater.regenerate_all()
