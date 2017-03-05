import scanner

source_dir = '/home/robbie/Music/'
dest_dir = '/home/robbie/Documents/test/'
options = {
    'format': 'mp3',
    'bitrate': 320
}


def main():
    scanner.tree_scanner(source_dir, dest_dir, options)

if __name__ == "__main__":
    main()
