import scanner
import configparser
from os.path import expanduser

config = configparser.ConfigParser()
config.read('config/config.ini')

source_dir = expanduser(config['PATH']['input'])
dest_dir = expanduser(config['PATH']['output'])
options = {
    'format': config['AUDIO']['format'],
    'bitrate': config['AUDIO']['bitrate']
}

def main():
    scanner.tree_scanner(source_dir, dest_dir, options)

if __name__ == "__main__":
    main()
