import os
import logging
import shutil
import hashlib
import shlex
from multiprocessing import Pool
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
options = {}
ffmpeg_args = ''


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
        global ffmpeg_args
        ffmpeg_args = ffmpeg_arg_generator()

        pool = Pool(processes=options['thread_count'])
        pool.map(convert, self.jobs)
        pool.close()
        pool.join()


'''Converts files using the command line and ffmpeg. Called in a pool as a multiprocess, meaning multiple copies
of these function may run concurrently. Due to constraints of the multiprocessing pool, this function is only 
allowed one input variable.'''


def convert(job):
    fqfn_input = job['input_file']
    fqfn_output = job['output_file']
    global ffmpeg_args

    # Do the conversion
    try:
        log.info("Converting file '%s'." % fqfn_input)
        if options['custom_command'] != '':
            first = options['custom_command'].rsplit('[INPUT]')[0]  # Before INPUT file
            second = options['custom_command'].split('[INPUT]')[1].rsplit('[OUTPUT]')[0]  # After INPUT & before OUTPUT
            third = options['custom_command'].split('[INPUT]')[1].rsplit('[OUTPUT]')[1]  # After OUTPUT
            command = first + shlex.quote(fqfn_input) + second + shlex.quote(fqfn_output) + third
        else:
            command = 'ffmpeg -i ' + shlex.quote(fqfn_input) + ' ' + ffmpeg_args + ' ' + shlex.quote(fqfn_output)\
                  + '>/dev/null 2>&1'
        os.system(command)
        return
    except Exception as e:
        print(e)
        log.warning("Failed to convert file: '%s'." % fqfn_output)


'''Using the globaloptions variable, this function will generate and return the proper ffmpeg
command-line arguments based on the given codec / bitrate configuration'''


def ffmpeg_arg_generator():
    global options
    ffmpeg_args = ''
    bitrate = int(options['bitrate'])

    if options['format'] == 'mp3':
        if options['bitrate_type'] == 'cbr':
            ffmpeg_args += '-b:a ' + options['bitrate'] + 'k'

        if options['bitrate_type'] == 'vbr':
            if bitrate >= 250:
                quality = '0'
            elif bitrate in range(210, 250):
                quality = '1'
            elif bitrate in range(180, 210):
                quality = '2'
            elif bitrate in range(165, 180):
                quality = '3'
            elif bitrate in range(145, 165):
                quality = '4'
            elif bitrate in range(125, 145):
                quality = '5'
            elif bitrate in range(107, 125):
                quality = '6'
            elif bitrate in range(93, 107):
                quality = '7'
            elif bitrate in range(70, 93):
                quality = '8'
            else:
                quality = '9'
            ffmpeg_args += '-q:a ' + quality

    elif options['format'] == 'aac':
        ffmpeg_args += '-c:a aac '
        if options['bitrate_type'] == 'cbr':
            ffmpeg_args += '-b:a ' + options['bitrate'] + 'k'

        if options['bitrate_type'] == 'vbr':
            if bitrate >= 250:
                quality = '2'
            elif bitrate in range(70, 250):
                # Ffmpeg allows args from 0.1 to 2 for AAC. Assuming this scale is linear, this takes the sensible
                # bitrates between those values and uses a regression and rounding to get a value between 0.1 and 2
                quality = round(-0.638889 + 0.0105556 * bitrate, 2)
            else:
                quality = '0.1'
            ffmpeg_args += '-q:a ' + quality

    return ffmpeg_args
