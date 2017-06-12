import sys
import shutil
import logging
import scanner
import option_parser
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

options = option_parser.options()
input_dir = option_parser.input_dir()
output_dir = option_parser.output_dir()

''' Parse command-line arguments '''
# Delete all contents of output folder
if '--purge' in sys.argv:
    log.info("Purging all files in directory: '%s'." % output_dir)
    shutil.rmtree(output_dir)


def main():
    scanner.Scanner(input_dir, output_dir, options)

if __name__ == "__main__":
    main()
