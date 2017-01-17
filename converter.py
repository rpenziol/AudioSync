import os
import logging
import shutil
import ffmpy
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


'''Use FFmpeg wrapper to convert file from input_file to output_file destination.
Grab formatting options from 'options' JSON
'''


def convert(input_file='', output_file='', options=None):
    input_file_base, input_extension = os.path.splitext(input_file)

    # Check if file exists
    if os.path.isfile(output_file):
        log.info("File '%s' already exists. Skipping." % (output_file))
        return

    # Simply copy non-media files
    if input_extension != '.flac':
        try:
            shutil.copy2(input_file, output_file)

        except Exception as e:
            print(e)
            log.warning("Insufficient priveledges to write file: '%s'." % (output_file))

        return

    # Do the conversion
    try:
        ff = ffmpy.FFmpeg(
            inputs={input_file: None},
            outputs={output_file: '-ab 320k'}
        )
        ff.run()

    except Exception as e:
        print(e)
        log.warning("Insufficient priveledges to write file: '%s'." % (output_file))

    return


