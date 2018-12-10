import sys
import os
import shutil
import logging
import scanner
import option_parser
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main():
    log.info('WELCOME TO AUDIOSYNC')
    options = option_parser.options()
    input_dir = option_parser.input_dir()
    output_dir = option_parser.output_dir()

    if '--purge' in sys.argv:
        log.info('Purging all files in directory: "{0}".'.format(output_dir))

        # Delete all folder contents without deleting output_dir folder
        for item in os.listdir(output_dir):
            full_path = os.path.join(output_dir, item)
            if os.path.isfile(full_path):
                os.unlink(full_path)
            else:
                shutil.rmtree(full_path)

    scanner.Scanner(input_dir, output_dir, options)
    log.info('DONE SYNCING DIRECTORIES. EXITING.')


if __name__ == '__main__':
    main()
