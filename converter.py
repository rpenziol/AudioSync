import os
import logging
import shutil
import hashlib
import shlex
from multiprocessing import Pool
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
options = {}


def convert(job):
    fqfn_input = job['input_file']
    fqfn_output = job['output_file']
    # Do the conversion
    try:
        log.info("Converting file '%s'." % fqfn_input)
        command = 'ffmpeg -i ' + shlex.quote(fqfn_input) + ' -ab ' + shlex.quote(options['bitrate']) + 'k' \
                  ' -map_metadata 0 -id3v2_version 3 ' + shlex.quote(fqfn_output) + '>/dev/null 2>&1'
        os.system(command)
        return
    except Exception as e:
        print(e)
        log.warning("Failed to convert file: '%s'." % fqfn_output)


class Converter(object):

    # Attributes:
    db = None
    files = []
    jobs = []

    def __init__(self, db, init_options):
        self.db = db
        global options
        options = init_options

    def queue_job(self, input_file, output_file):
        file = {
            'input_file': input_file,
            'output_file': output_file
        }
        self.files.append(file)

    def process_queue(self):
        for file in self.files:
            fqfn_input = file['input_file']
            fqfn_output = file['output_file']
            fqfn_input_base, input_extension = os.path.splitext(fqfn_input)
            fqfn_input_md5 = hashlib.md5(open(fqfn_input, 'rb').read()).hexdigest()
            hash_match = False
            output_exists = False

            # Check if input file hash matches in database
            if self.db.get_hash(fqfn_input) == fqfn_input_md5:
                hash_match = True

            # Check if output file exists
            if os.path.isfile(fqfn_output):
                output_exists = True

            # Output file up-to-date
            if hash_match and output_exists:
                log.debug("Output file '%s' up-to-date. Skipping." % fqfn_output)
                continue

            # Output file removed
            if hash_match and not output_exists:
                log.debug("Output file '%s' has been removed. Reprocessing." % fqfn_output)

            # Output file outdated
            if not hash_match and output_exists:
                log.debug("Output file '%s' is outdated. Deleting and reprocessing." % fqfn_output)
                os.remove(fqfn_output)
                self.db.update(fqfn_input, fqfn_input_md5)

            # New input file
            if not hash_match and not output_exists:
                log.debug("Input file '%s' is new. Adding to processing list." % fqfn_input)
                self.db.update(fqfn_input, fqfn_input_md5)

            # Simply copy non-audio files
            if input_extension.lstrip('.') not in options['extensions_to_convert']:
                try:
                    log.info("Copying '%s' to '%s'" % (fqfn_input, fqfn_output))
                    shutil.copy2(fqfn_input, fqfn_output)
                    continue  # No need to add to convert queue
                except Exception as e:
                    print(e)
                    log.warning("Unable to copy file: '%s'." % fqfn_output)

            self.jobs.append(file)
        # End for

        pool = Pool(processes=options['thread_count'])
        pool.map(convert, self.jobs)
        pool.close()
        pool.join()
