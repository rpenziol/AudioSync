import os
import logging
import shutil
import hashlib
import shlex
from multiprocessing import Pool
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class Converter(object):

    # Attributes:
    db = None
    options = {}
    queue = []

    def __init__(self, db, options):
        self.db = db
        self.options = options

    def queue_job(self, input_file, output_file):
        job = {
            'input_file': input_file,
            'output_file': output_file
        }
        self.queue.append(job)

    def process_queue(self):
        pool = Pool(processes=1)
        for job in self.queue:
            self.convert(job['input_file'], job['output_file'])

    ''' Use FFmpeg wrapper to convert file from fqfn_input to fqfn_output destination.
    Grab formatting options from options JSON '''
    def convert(self, fqfn_input='', fqfn_output=''):
        fqfn_input_base, input_extension = os.path.splitext(fqfn_input)
        fqfn_input_md5 = hashlib.md5(open(fqfn_input, 'rb').read()).hexdigest()
        hash_match = False

        # Check if file hash is in the database
        try:
            if self.db.select(fqfn_input) == fqfn_input_md5:
                hash_match = True
        except Exception as e:
            log.debug(e)
            log.debug("File '%s' hash not in database" % fqfn_input)

        # Check if output file exists and is up to date
        if hash_match and os.path.isfile(fqfn_output):
            log.debug("File '%s' already exists. Skipping." % fqfn_output)
            return

        # Check if output file exists and remove it, as it's outdated
        if os.path.isfile(fqfn_output):
            log.info("File '%s' is outdated. Deleting." % fqfn_output)
            os.remove(fqfn_output)

        # Store/update hash
        self.db.insert(fqfn_input, fqfn_input_md5)

        # Simply copy non-audio files
        if input_extension != '.flac':
            try:
                log.info("Copying '%s' to '%s'" % (fqfn_input, fqfn_output))
                shutil.copy2(fqfn_input, fqfn_output)
            except Exception as e:
                print(e)
                log.warning("Insufficient privileges to write file: '%s'." % fqfn_output)
            return

        # Do the conversion
        try:
            log.info("Converting file '%s'." % fqfn_input)
            command = 'ffmpeg -i ' + shlex.quote(fqfn_input) + ' -ab 320k -map_metadata 0 -id3v2_version 3 ' + \
                      shlex.quote(fqfn_output) + '>/dev/null 2>&1'
            os.system(command)

        except Exception as e:
            print(e)
            log.warning("Insufficient privileges to write file: '%s'." % fqfn_output)

        return
