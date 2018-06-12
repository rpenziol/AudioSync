import os.path
import logging
import hashlib
from tinydb import TinyDB, Query
log = logging.getLogger(__name__)


class Database(object):
    def __init__(self, database_path):
        self._db = self.load_database(database_path)

    @staticmethod
    def load_database(database_path):
        # Use MD5 of source_path to establish database name
        db_name = hashlib.md5(str(database_path).encode('utf-8')).hexdigest() + '.json'
        current_path = os.path.dirname(os.path.realpath(__file__))
        db_dir = os.path.join(current_path, 'db')

        if not os.path.exists(db_dir):
            log.info("Directory '{0}' does't exist. Creating directory".format(db_dir))
            os.makedirs(db_dir)
        else:
            log.debug("Directory '{0}' already exist. Skipping directory creation.".format(db_dir))

        db_full_path = os.path.join(db_dir, db_name)
        return TinyDB(db_full_path)

    ''' Take key/value pair and store/update value in database '''
    def update(self, path='', hash='', mtime='', size=0):
        file = Query()
        if self._db.count(file.path == path) >= 1:
            self._db.update({'path': path, 'hash': hash, 'mtime': mtime, 'size': size}, file.path == path)
        else:
            self._db.insert({'path': path, 'hash': hash, 'mtime': mtime, 'size': size})

    ''' Lookup key in database, return value '''
    def get_property(self, path, prop):
        file_property = ''
        file = Query()
        if self._db.count(file.path == path) >= 1:
            file_property = self._db.search(file.path == path)[0][prop]
        return file_property
