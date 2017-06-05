import sys
import shutil
import multiprocessing
import logging
import configparser
from os.path import expanduser
import scanner
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

''' Read in from configuration file '''
config = configparser.ConfigParser()
config.read('config/config.ini')

source_dir = expanduser(config['PATH']['input'])
dest_dir = expanduser(config['PATH']['output'])

# Parse extension
extension = config['AUDIO']['output_format']
if config['AUDIO']['output_format'] == 'aac':
    extension = 'm4a'

# Parse bitrate type
if not (config['AUDIO']['bitrate_type'] == 'vbr' or config['AUDIO']['bitrate_type'] == 'cbr'):
    log.fatal("Invalid bitrate type: '%s'. Valid options: 'cbr' or 'vbr'" % config['AUDIO']['bitrate_type'])
    exit(1)

# Parse thread count
thread_count = 1
try:
    if config['ADVANCE']['thread_count'] == 'max':
        thread_count = multiprocessing.cpu_count()
    elif int(config['ADVANCE']['thread_count']) <= 0:
        thread_count = 1
    else:
        thread_count = int(config['ADVANCE']['thread_count'])
except Exception as e:
    log.fatal("Invalid number of threads: '%s'." % config['ADVANCE']['thread_count'])
    exit(1)



options = {
    'format': config['AUDIO']['output_format'],
    'bitrate': config['AUDIO']['bitrate'],
    'bitrate_type': config['AUDIO']['bitrate_type'],
    'extensions_to_convert': config['AUDIO']['extensions_to_convert'].split(','),  # Create list
    'thread_count': thread_count,
    'extension': extension
}

''' Parse command-line arguments '''
# Delete all contents of output folder
if '--purge' in sys.argv:
    log.info("Purging all files in directory: '%s'." % dest_dir)
    shutil.rmtree(dest_dir)


def main():
    scanner.Scanner(source_dir, dest_dir, options)

if __name__ == "__main__":
    main()
