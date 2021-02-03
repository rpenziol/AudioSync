import multiprocessing
import logging
import yaml
from os.path import expanduser
log = logging.getLogger(__name__)


def options():
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, yaml.SafeLoader)

    # Set output extension based on codec used
    extension = config['audio']['output_format']
    if config['audio']['output_format'] == 'aac' or config['audio']['output_format'] == 'alac':
        extension = 'm4a'

    # Parse sample rate
    sample_rate = '44100'
    if config['audio']['sample_rate'] == 'unchanged':
        sample_rate = None
    else:
        if 0 < int(config['audio']['sample_rate']) <= 5644800:
            sample_rate = config['audio']['sample_rate']
        else:
            log.fatal('Unsupported sample_rate: "{0}". '
                      'Valid options are "unchanged" or a number between 1 and 5644800, inclusive.'.format(
                        config['audio']['sample_rate']))
            exit(1)

    # Parse sample rate
    if not config['audio']['bitrate_type'] in ('cbr', 'vbr'):
        log.fatal('Invalid bitrate type: "{0}". Valid options: "cbr" or "vbr"'.format(config['audio']['bitrate_type']))
        exit(1)

    # Parse thread count
    if config['advance']['thread_count'] == 'max':
        thread_count = multiprocessing.cpu_count()
    else:
        thread_count = config['advance']['thread_count']

    # Parse match_method type
    if not (config['advance']['match_method'] == 'date_size' or config['advance']['match_method'] == 'hash'):
        log.fatal('Invalid match method: "{0}". Valid options: "date_size" or "hash"'.format(
            config['advance']['match_method']))
        exit(1)

    # Parse extensions to ignore completely
    extensions_to_ignore = []
    if config['advance']['extensions_to_ignore'] != '':
        extensions_to_ignore = config['advance']['extensions_to_ignore'].lower().replace(' ', '').split(',')

    # Parse custom command
    custom_command = ''
    if config['advance']['enable_custom_command'] == 'true':
        custom_command = config['ADVANCE']['custom_command']
        if '[INPUT]' not in custom_command or '[OUTPUT]' not in custom_command:
            log.fatal('Custom command does not contain [INPUT] or [OUTPUT] string argument.')
            exit(1)

    return {
        'format': config['audio']['output_format'],
        'bitrate': config['audio']['bitrate'],
        'bitrate_type': config['audio']['bitrate_type'],
        'sample_rate': sample_rate,
        'extensions_to_convert': config['audio']['extensions_to_convert'].lower().replace(' ', '').split(','),
        'ffmpeg_path': config['path']['ffmpeg'],
        'thread_count': thread_count,
        'match_method': config['advance']['match_method'],
        'extensions_to_ignore': extensions_to_ignore,
        'extension': extension,
        'custom_command': custom_command
    }


def input_dir():
    with open('config.yaml', 'r') as f:
        return expanduser(yaml.load(f, yaml.SafeLoader)['path']['input'])


def output_dir():
    with open('config.yaml', 'r') as f:
        return expanduser(yaml.load(f, yaml.SafeLoader)['path']['output'])
