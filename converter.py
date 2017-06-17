import os
import subprocess
import logging
import shutil
import hashlib
import shlex
from multiprocessing import Pool
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
options = {}


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
            'output_file': output_file,
            # These must be added to every item in the 'files' list due to Windows being unable to access global
            # variables in a process spawned from 'multiprocess', and they must be accessible to convert()
            'ffmpeg_path': options['ffmpeg_path'],
            'ffmpeg_args': ffmpeg_arg_generator(),
            'custom_command': options['custom_command']
        }
        self.files.append(file)

    def process_queue(self):
        for file in self.files:
            fqfn_input = file['input_file']
            fqfn_output = file['output_file']
            fqfn_input_base, input_extension = os.path.splitext(fqfn_input)
            fqfn_input_md5 = 0
            fqfn_input_mtime = os.path.getmtime(fqfn_input)
            fqfn_input_size = os.path.getsize(fqfn_input)
            match = False
            output_exists = False

            # Process file matches either on date modified & size, or by hash
            if options['match_method'] == 'date_size':
                # Check if input file matches in database
                if self.db.get_property(fqfn_input, 'mtime') == fqfn_input_mtime \
                        and self.db.get_property(fqfn_input, 'size') == fqfn_input_size:
                    match = True
            elif options['match_method'] == 'hash':
                fqfn_input_md5 = hashlib.md5(open(fqfn_input, 'rb').read()).hexdigest()
                if self.db.get_hash(fqfn_input) == fqfn_input_md5:
                    match = True
            else:
                log.fatal("No match method set.")
                exit(1)

            # Check if output file exists
            if os.path.isfile(fqfn_output):
                output_exists = True

            # Output file up-to-date
            if match and output_exists:
                log.debug("Output file '%s' up-to-date. Skipping." % fqfn_output)
                continue

            # Output file removed
            if match and not output_exists:
                log.debug("Output file '%s' has been removed. Reprocessing." % fqfn_output)

            # Output file outdated
            if not match and output_exists:
                log.debug("Output file '%s' is outdated. Deleting and reprocessing." % fqfn_output)
                os.remove(fqfn_output)
                self.db.update(fqfn_input, fqfn_input_md5, fqfn_input_mtime, fqfn_input_size)

            # New input file
            if not match and not output_exists:
                log.debug("Input file '%s' is new. Adding to processing list." % fqfn_input)
                self.db.update(fqfn_input, fqfn_input_md5, fqfn_input_mtime, fqfn_input_size)

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

        # Empty list of files. Allows 'process_queue' to be called in succession on same instance of Converter class
        self.files = []


'''Converts files using the command line and ffmpeg. Called in a pool as a multiprocess, meaning multiple copies
of these function may run concurrently. Due to constraints of the multiprocessing pool, this function is only 
allowed one input variable.'''


def convert(job):
    fqfn_input = job['input_file']
    fqfn_output = job['output_file']
    ffmpeg_path = job['ffmpeg_path']
    custom_command = job['custom_command']
    ffmpeg_args = job['ffmpeg_args']

    # Do the conversion
    try:
        log.info("Converting file '%s'." % fqfn_input)

        if custom_command != '':
            command_list = custom_command.split()
            command_list[command_list.index('[INPUT]')] = fqfn_input  # Replace index with [INPUT] to actual path
            command_list[command_list.index('[OUTPUT]')] = fqfn_output  # Replace index with [OUTPUT] to actual path
        else:
            command_list = [ffmpeg_path, "-i", fqfn_input]
            command_list.extend(ffmpeg_args)
            command_list.append(fqfn_output)

        FNULL = open(os.devnull, 'w')  # Redirect FFMPEG output to /dev/null
        subprocess.call(command_list, stdout=FNULL, stderr=FNULL, shell=False)
        return
    except Exception as e:
        print(e)
        log.warning("Failed to convert file: '%s'." % fqfn_output)


'''Using the globaloptions variable, this function will generate and return the proper ffmpeg
command-line arguments based on the given codec / bitrate configuration'''


def ffmpeg_arg_generator():
    global options
    ffmpeg_args = []
    bitrate = int(options['bitrate'])

    if options['format'] == 'mp3':
        if options['bitrate_type'] == 'cbr':
            ffmpeg_args.extend(['-b:a', options['bitrate'] + 'k'])

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
            ffmpeg_args.extend(['-q:a', quality])

    elif options['format'] == 'aac':
        ffmpeg_args.extend(['-c:a aac '])
        if options['bitrate_type'] == 'cbr':
            ffmpeg_args.extend(['-b:a', options['bitrate'] + 'k'])

        if options['bitrate_type'] == 'vbr':
            if bitrate >= 250:
                quality = '2'
            elif bitrate in range(70, 250):
                # Ffmpeg allows args from 0.1 to 2 for AAC. Assuming this scale is linear, this takes the sensible
                # bitrates between those values and uses a regression and rounding to get a value between 0.1 and 2
                quality = round(-0.638889 + 0.0105556 * bitrate, 2)
            else:
                quality = '0.1'
            ffmpeg_args.extend(['-q:a ', quality])

    return ffmpeg_args
