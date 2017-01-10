import ffmpy
import os
import shutil
import watchdog
import logging

input_dir = '/home/robbie/Music/'
output_dir = '/home/robbie/Documents/test/'

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

for root, dirs, files_junk in os.walk(input_dir, topdown=True):
    for directory in dirs:
        rel_root = root.replace(input_dir, '')
        rel_path = os.path.join(rel_root, directory)
        input_path = os.path.join(input_dir, rel_path)
        output_path = os.path.join(output_dir, rel_path)

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
        for root_junk, dirs_junk, files in os.walk(input_path, topdown=True):
            for file in files:
                input_file = os.path.join(input_path, file)
                output_file = os.path.join(output_path, file)

                if not os.path.isfile(output_file):
                    log.info("File '%s' does't exist. Converting input file." % (output_file))
                    try:
                        shutil.copy2(input_file, output_file)
                        print("Conversion code goes here.")
                        
                        # ff = ffmpy.FFmpeg(inputs={input_file: None}, outputs={output_file + '.mp3': '-ab 320k'})
                        # ff.run()
                    except Exception as e:
                        print(e)
                        log.warning("Insufficient priveledges to create directory '%s'." % (output_file))
                else:
                    log.debug("Directory '%s' already exist. Skipping file conversion." % (output_file))
