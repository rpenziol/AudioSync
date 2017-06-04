import sys
import shutil
import configparser
from os.path import expanduser
import scanner


''' Read in from configuration file '''
config = configparser.ConfigParser()
config.read('config/config.ini')

source_dir = expanduser(config['PATH']['input'])
dest_dir = expanduser(config['PATH']['output'])
options = {
    'format': config['AUDIO']['output_format'],
    'bitrate': config['AUDIO']['bitrate'],
    'extensions_to_convert': config['AUDIO']['extensions_to_convert'].split(',')  # Create list
}

''' Parse command-line arguments '''
# Delete all contents of output folder
if '--purge' in sys.argv:
    shutil.rmtree(dest_dir)


def main():
    scanner.Scanner(source_dir, dest_dir, options)

if __name__ == "__main__":
    main()
