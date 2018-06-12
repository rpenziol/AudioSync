import os
import subprocess
import logging
import shutil
import hashlib
from multiprocessing import Pool
log = logging.getLogger(__name__)


class Converter(object):
    def __init__(self, db, options):
        self._files = []
        self._jobs = []
        self._db = db
        self._options = options
        self._ffmpeg_args = self.ffmpeg_arg_generator()

    def queue_job(self, input_file, output_file):
        file = {
            'input_file': input_file,
            'output_file': output_file,
            'ffmpeg_path': self._options['ffmpeg_path'],
            'ffmpeg_args': self._ffmpeg_args,
            'custom_command': self._options['custom_command']
        }
        self._files.append(file)

    def process_queue(self):
        for file in self._files:
            fqfn_input = file['input_file']
            fqfn_output = file['output_file']
            fqfn_input_base, input_extension = os.path.splitext(fqfn_input)
            fqfn_input_md5 = 0
            fqfn_input_mtime = os.path.getmtime(fqfn_input)
            fqfn_input_size = os.path.getsize(fqfn_input)
            match = False
            output_exists = False

            # Process file matches either on date modified & size, or by hash
            if self._options['match_method'] == 'date_size':
                # Check if input file matches in database
                if self._db.get_property(fqfn_input, 'mtime') == fqfn_input_mtime \
                        and self._db.get_property(fqfn_input, 'size') == fqfn_input_size:
                    match = True
            elif self._options['match_method'] == 'hash':
                fqfn_input_md5 = hashlib.md5(open(fqfn_input, 'rb').read()).hexdigest()
                if self._db.get_hash(fqfn_input) == fqfn_input_md5:
                    match = True
            else:
                log.fatal('No match method set.')
                exit(1)

            if os.path.isfile(fqfn_output):
                output_exists = True
                if os.path.getsize(fqfn_output) == 0:
                    match = False

            if match and output_exists:
                log.debug('Output file "{0}" up-to-date. Skipping.'.format(fqfn_output))
                continue

            if match and not output_exists:
                log.debug('Output file "{0}" has been removed. Reprocessing.'.format(fqfn_output))

            if not match and output_exists:
                log.debug('Output file "{0}" is outdated. Deleting and reprocessing.'.format(fqfn_output))
                os.remove(fqfn_output)
                self._db.update(fqfn_input, fqfn_input_md5, fqfn_input_mtime, fqfn_input_size)

            if not match and not output_exists:
                log.debug('Input file "{0}" is new. Adding to processing list.'.format(fqfn_input))
                self._db.update(fqfn_input, fqfn_input_md5, fqfn_input_mtime, fqfn_input_size)

            # Simply copy non-audio files
            if input_extension.lstrip('.').lower() not in self._options['extensions_to_convert']:
                try:
                    log.info('Copying "{0}" to "{1}"'.format(fqfn_input, fqfn_output))
                    shutil.copy2(fqfn_input, fqfn_output)
                    continue  # No need to add to convert queue
                except Exception as e:
                    print(e)
                    log.warning('Unable to copy file: "{0}".'.format(fqfn_output))

            self._jobs.append(file)

        pool = Pool(processes=self._options['thread_count'])
        pool.map(convert, self._jobs)
        pool.close()
        pool.join()

    '''Using the globaloptions variable, this function will generate and return the proper ffmpeg
    command-line arguments based on the given codec / bitrate configuration'''
    def ffmpeg_arg_generator(self):
        ffmpeg_args = ['-vf', 'scale=-2:500']  # Scale album art to height of 500px
        if self._options['sample_rate']:
            ffmpeg_args.extend(['-ar', str(self._options['sample_rate'])])

        bitrate = int(self._options['bitrate'])

        if self._options['format'] == 'mp3':
            if self._options['bitrate_type'] == 'cbr':
                ffmpeg_args.extend(['-b:a', str(self._options['bitrate']) + 'k'])

            if self._options['bitrate_type'] == 'vbr':
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

        elif self._options['format'] == 'aac':
            ffmpeg_args.extend(['-c:a', 'aac'])
            if self._options['bitrate_type'] == 'cbr':
                ffmpeg_args.extend(['-b:a', self._options['bitrate'] + 'k'])

            if self._options['bitrate_type'] == 'vbr':
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


'''Converts files using the command line and ffmpeg. Called in a pool as a multiprocess, meaning multiple copies
of these function may run concurrently. Due to constraints of the multiprocessing pool, this function is only 
allowed one input variable.'''


def convert(job):
    fqfn_input = job['input_file']
    fqfn_output = job['output_file']
    ffmpeg_path = job['ffmpeg_path']
    custom_command = job['custom_command']
    ffmpeg_args = job['ffmpeg_args']

    log.info('Converting file "{0}" to "{1}"'.format(fqfn_input, fqfn_output))

    if custom_command != '':
        command_list = custom_command.split()
        command_list[command_list.index('[INPUT]')] = fqfn_input
        command_list[command_list.index('[OUTPUT]')] = fqfn_output
    else:
        command_list = [ffmpeg_path, '-i', fqfn_input]
        command_list.extend(ffmpeg_args)
        command_list.append(fqfn_output)

    fnull = open(os.devnull, 'w')  # Redirect FFMPEG output to /dev/null
    subprocess.call(command_list, stdout=fnull, stderr=fnull, shell=False)
