import os.path
import logging
import hashlib
from tinydb import TinyDB, Query
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class Database(object):

    # Attributes:
    db = None  # Database file handle

    def __init__(self, database_path):
        self.load_database(database_path)

    def load_database(self, database_path=None):
        # Need a source_path to establish database's name
        if not database_path:
            log.fatal("No source_path argument given to load database")
            exit()

        # Use MD5 of source_path to establish database name
        db_name = hashlib.md5(str(database_path).encode('utf-8')).hexdigest() + '.json'
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
        self.db = TinyDB(db_full_path)

    ''' Take key/value pair and store/update value in database '''
    def update(self, path='', hash=''):
        file = Query()
        # If file hash is present, update the hash
        if self.db.count(file.path == path) >= 1:
            self.db.update({'path': path, 'hash': hash}, file.path == path)
        # Otherwise insert the hash for the 1st time
        else:
            self.db.insert({'path': path, 'hash': hash})

    ''' Lookup key in database, return value '''
    def get_hash(self, path=''):
        file_hash = ''
        file = Query()
        # Get hash if path in db, else return empty string
        if self.db.count(file.path == path) >= 1:
            file_hash = self.db.search(file.path == path)[0]['hash']
        return file_hash
