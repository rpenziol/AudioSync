import os
import converter
import shutil
import database
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


''' Recursively scans input directory structure and compares to the destination folder tree.
Creates missing directories in destination folder, and calls dir_scanner to sync files
'''


def tree_scanner(source_dir='', dest_dir='', options=None):
    db_name = database.load_database(source_dir)

    for root, dirs, files_junk in os.walk(source_dir, topdown=True):
        for directory in dirs:
            rel_root = root.replace(source_dir, '')
            rel_path = os.path.join(rel_root, directory)
            input_path = os.path.join(source_dir, rel_path)
            output_path = os.path.join(dest_dir, rel_path)

            # Create directory
            if not os.path.exists(output_path):
                log.info("Directory '%s' does't exist. Creating directory" % (output_path))
                try:
                    os.makedirs(output_path)
                except Exception as e:
                    print(e)
                    log.warning("Insufficient privileges to create directory '%s'." % (output_path))

            else:
                log.debug("Directory '%s' already exist. Skipping directory creation." % (output_path))

            dir_scanner(input_path, output_path, options)


''' Compares files between input and output paths.
Depending on file type, copy or convert file from input_path to output_path
'''


def dir_scanner(input_path='', output_path='', options=None):
        # Remove orphaned files and folder trees from output_path
        remove_orphan_dirs(input_path, output_path)
        remove_orphan_files(input_path, output_path)

        # Convert files in current directory
        for item in os.listdir(input_path):
            if not os.path.isfile(os.path.join(input_path, item)):
                log.debug("'%s' is a directory. Skipping conversion." % (item))
                continue

            # Create full file path for input and output
            base_filename, input_extension = os.path.splitext(item)
            input_file = os.path.join(input_path, item)
            output_file = os.path.join(output_path, item)

            if input_extension == '.flac':
                output_filename = base_filename + '.' + options[format]
                output_file = os.path.join(output_path, output_filename)

            converter.convert(input_file, output_file, options)


''' Remove folder trees from output_path if folder isn't in input_path'''


def remove_orphan_dirs(input_path='', output_path=''):

    for item in os.listdir(output_path):
        # If item is a directory
        if not os.path.isfile(os.path.join(output_path, item)):
            # If directory is orphaned
            if not os.path.exists(os.path.join(input_path, item)):
                log.debug("'{0}' is an orphaned directory. Removing from '{1}'.".format(item, output_path))
                try:
                    shutil.rmtree(os.path.join(output_path, item))
                except Exception as e:
                    print(e)
                    log.warning("Failed to remove folder '{0}'.".format(os.path.join(output_path, item)))


''' Remove files from output_path if file isn't in input_path'''


def remove_orphan_files(input_path='', output_path=''):
    # Store list of file names (without extensions) from input_path
    input_files = []

    # Collect list of file names from input_path
    for item in os.listdir(input_path):
        if os.path.isfile(os.path.join(input_path, item)):
            # Strip file extension
            base_name = os.path.splitext(item)[0]
            input_files.append(base_name)

    # Remove orphaned files from output_path
    for item in os.listdir(output_path):
        if os.path.isfile(os.path.join(output_path, item)):
            # Strip file extension
            base_name = os.path.splitext(item)[0]
            # If file is orphaned
            if base_name not in input_files:
                log.debug("'{0}' is an orphaned file. Removing from '{1}'.".format(item, output_path))
                try:
                    os.remove(os.path.join(output_path, item))
                except Exception as e:
                    print(e)
                    log.warning("Failed to remove file '{0}'.".format(os.path.join(output_path, item)))
