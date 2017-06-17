import time
import os
import logging
import scanner
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class Watcher:
    def __init__(self, source_dir, dest_dir, options):
        self.observer = Observer()
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.scanner = scanner.Scanner(source_dir, dest_dir, options)

    def run(self):
        event_handler = Handler(self.scanner)
        self.observer.schedule(event_handler, self.source_dir, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            log.debug("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, scanner):
        self.scanner = scanner

    ''' On dir: Create folder in output_dir
        On file: Get details, add to database, convert '''
    def on_created(self, event):
        input_path, filename = os.path.split(event.src_path)
        output_path = self.scanner.dest_dir + input_path.replace(self.scanner.source_dir, '')
        self.scanner.queue_file(input_path, output_path, filename)
        self.scanner.process_queue()
        log.debug("Received created event - %s." % event.src_path)

    ''' On dir: Delete output dir, remove files from database
        On file: Delete file from database, delete output_dir's file '''
    def on_deleted(self, event):
        log.debug("Received deleted event - %s." % event.src_path)

    ''' On dir: File under folder has changed. No action necessary
        On file: Delete output_dir's file, update database, reconvert '''
    def on_modified(self, event):
        if event.is_directory:
            log.debug("Received modified event on directory - %s. Skipping action." % event.src_path)
            return

        # Taken any action here when a file is modified.
        log.debug("Received modified event - %s." % event.src_path)

    ''' On dir: 
        On file: Find in database, rename and update in database, send rename command on output_file'''
    def on_moved(self, event):
        log.debug("Received moved event - {0} to {1}".format(event.src_path, event.dest_path))


if __name__ == '__main__':
    w = Watcher()
    w.run()
