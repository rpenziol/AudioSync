import os
import logging
import shutil
import hashlib
import shlex
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


'''Use FFmpeg wrapper to convert file from input_file to output_file destination.
Grab formatting options from 'options' JSON
'''


def convert(input_file='', output_file='', db='', options=None):
    input_file_base, input_extension = os.path.splitext(input_file)
    input_file_md5 = hashlib.md5(open(input_file, 'rb').read()).hexdigest()
    hash_match = False

    # Check if file hash is in the database
    try:
        if db[input_file] == input_file_md5:
            hash_match = True
    except Exception as e:
        log.debug(e)
        log.debug("File '%s' hash not in database" % (input_file))

    # Check if output file exists and is up to date
    if hash_match and os.path.isfile(output_file):
        log.debug("File '%s' already exists. Skipping." % (output_file))
        return

    # Check if output file exists and remove it, as it's outdated
    if os.path.isfile(output_file):
        log.info("File '%s' is outdated. Deleting." % (output_file))
        os.remove(output_file)

    # Store/update hash
    db[input_file] = input_file_md5

    # Simply copy non-audio files
    if input_extension != '.flac':
        try:
            log.info("Copying '%s' to '%s'." % (input_file, output_file))
            shutil.copy2(input_file, output_file)
        except Exception as e:
            print(e)
            log.warning("Insufficient privileges to write file: '%s'." % (output_file))
        return

    # Do the conversion
    try:
        command = 'ffmpeg -i ' + shlex.quote(input_file) + ' -ab 320k -map_metadata 0 -id3v2_version 3 ' + shlex.quote(output_file)
        os.system(command)

    except Exception as e:
        print(e)
        log.warning("Insufficient privileges to write file: '%s'." % (output_file))

    return
