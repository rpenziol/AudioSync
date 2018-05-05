import multiprocessing
import logging
import configparser
from os.path import expanduser
log = logging.getLogger(__name__)


def options():
    # Read in from configuration file
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    # Set output extension based on codec used
    extension = config['AUDIO']['output_format']
    if config['AUDIO']['output_format'] == 'aac' or config['AUDIO']['output_format'] == 'alac':
        extension = 'm4a'

    # Parse bitrate type
    sample_rate = '44100'
    if config['AUDIO']['sample_rate'] == 'unchanged':
        sample_rate = None
    else:
        try:
            if 0 < int(config['AUDIO']['sample_rate']) <= 5644800:
                sample_rate = config['AUDIO']['sample_rate']
        except Exception as ex:
            log.fatal('Unsupported sample_rate: "{0}". '
                      'Valid options are "unchanged" or a number between 1 and 5644800, inclusive.'.format(
                        config['AUDIO']['sample_rate']))
            exit(1)

    # Parse sample rate
    if not (config['AUDIO']['bitrate_type'] == 'vbr' or config['AUDIO']['bitrate_type'] == 'cbr'):
        log.fatal('Invalid bitrate type: "{0}". Valid options: "cbr" or "vbr"'.format(config['AUDIO']['bitrate_type']))
        exit(1)

    # Parse thread count
    thread_count = 1
    try:
        if config['ADVANCE']['thread_count'] == 'max':
            thread_count = multiprocessing.cpu_count()
        elif int(config['ADVANCE']['thread_count']) <= 0:
            thread_count = 1
        else:
            thread_count = int(config['ADVANCE']['thread_count'])
    except Exception as e:
        log.fatal('Invalid number of threads: "{0}".'.format(config['ADVANCE']['thread_count']))
        exit(1)

    # Parse match_method type
    if not (config['ADVANCE']['match_method'] == 'date_size' or config['ADVANCE']['match_method'] == 'hash'):
        log.fatal('Invalid match method: "{0}". Valid options: "date_size" or "hash"'.format(
            config['ADVANCE']['match_method']))
        exit(1)

    # Parse extensions to ignore completely
    extensions_to_ignore = []
    if config['ADVANCE']['extensions_to_ignore'] != '':
        extensions_to_ignore = config['ADVANCE']['extensions_to_ignore'].lower().split(', ')  # Create list

    # Parse custom command
    custom_command = ''
    if config['ADVANCE']['enable_custom_command'] == 'true':
        custom_command = config['ADVANCE']['custom_command']
        if '[INPUT]' not in custom_command and '[OUTPUT]' not in custom_command:
            log.fatal('Custom command does not contain [INPUT] or [OUTPUT] string argument.')
            exit(1)
        if '[INPUT]' not in custom_command:
            log.fatal('Custom command does not contain [INPUT] string argument.')
            exit(1)
        if '[OUTPUT]' not in custom_command:
            log.fatal('Custom command does not contain [OUTPUT] string argument.')
            exit(1)

    return {
        'format': config['AUDIO']['output_format'],
        'bitrate': config['AUDIO']['bitrate'],
        'bitrate_type': config['AUDIO']['bitrate_type'],
        'sample_rate': sample_rate,
        'extensions_to_convert': config['AUDIO']['extensions_to_convert'].lower().split(','),
        'ffmpeg_path': config['PATH']['ffmpeg'],
        'thread_count': thread_count,
        'match_method': config['ADVANCE']['match_method'],
        'extensions_to_ignore': extensions_to_ignore,
        'extension': extension,
        'custom_command': custom_command
    }


def input_dir():
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    return expanduser(config['PATH']['input'])


def output_dir():
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    return expanduser(config['PATH']['output'])
