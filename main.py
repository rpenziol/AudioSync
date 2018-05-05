import sys
import os
import shutil
import logging
import scanner
import option_parser
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

options = option_parser.options()
input_dir = option_parser.input_dir()
output_dir = option_parser.output_dir()


def main():
    if '--purge' in sys.argv:
        log.info("Purging all files in directory: '{0}'.".format(output_dir))

        # Delete all folder contents without deleting output_dir folder
        for item in os.listdir(output_dir):
            full_path = os.path.join(output_dir, item)
            if os.path.isfile(full_path):
                os.unlink(full_path)
            else:
                shutil.rmtree(full_path)

    scan = scanner.Scanner(input_dir, output_dir, options)
    scan.run()


if __name__ == "__main__":
    main()
