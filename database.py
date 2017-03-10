import os.path
import logging
import hashlib
from unqlite import UnQLite
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def load_database(source_path=None):
    # Need a source_path to establish database's name
    if not source_path:
        log.fatal("No source_path argument given to load database")
        exit()

    # Use MD5 of source_path to establish database name
    db_name = hashlib.md5(str(source_path).encode('utf-8')).hexdigest()
    current_path = os.path.dirname(os.path.realpath(__file__))
    db_dir = os.path.join(current_path, 'db')

    # Create directory for databases
    if not os.path.exists(db_dir):
        log.info("Directory '%s' does't exist. Creating directory" % (db_dir))
        try:
            os.makedirs(db_dir)
        except Exception as e:
            print(e)
            log.warning("Insufficient privileges to create directory '%s'." % (db_dir))
    else:
        log.debug("Directory '%s' already exist. Skipping directory creation." % (db_dir))

    db_full_path = os.path.join(db_dir, db_name)
    db = UnQLite(db_full_path)
    return db
