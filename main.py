import ffmpy
import os
import shutil
import watchdog
import logging
import converter

source_dir = '/home/robbie/Music/'
dest_dir = '/home/robbie/Documents/test/'
options = {
    format: 'mp3'
}

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

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
                log.warning("Insufficient priveledges to create directory '%s'." % (output_path))

        else:
            log.debug("Directory '%s' already exist. Skipping directory creation." % (output_path))

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
