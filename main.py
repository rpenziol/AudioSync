import ffmpy
import os
import watchdog
import logging

input_dir = 'D:\\'
output_dir = 'C:\\'

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

for root, dirs, files in os.walk(input_dir, topdown=False):
    for name in dirs:
        output_path = os.path.join(output_dir, name)

        if not os.path.exists(output_path):
            log.info("Directory '%s' does't exist. Creating directory" % (output_path))
            try:
                os.makedirs(output_path)
            except Exception as e:
                print(e)
                log.warning("Insufficient priveledges to create directory '%s'." % (output_path))

        else:
            log.debug("Directory '%s' already exist. Skipping directory creation." % (output_path))


    for name in files:
        output_file = os.path.join(output_dir, name)
        input_file = os.path.join(input_dir, name)

        if not os.path.isfile(output_file):
            log.info("File '%s' does't exist. Converting input file." % (output_file))
            try:
                ff = ffmpy.FFmpeg(inputs={input_file: None}, outputs={output_file + '.mp3': '-ab 320k'})
                ff.run()
                print("Conversion code goes here.")
            except Exception as e:
                print(e)
                log.warning("Insufficient priveledges to create directory '%s'." % (output_file))

        else:
            log.debug("Directory '%s' already exist. Skipping file conversion." % (output_file))
