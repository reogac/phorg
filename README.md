# phorg - a simple photo organizer

Phorg is a simple command line tool for organizing your photos into year/month folders. 

#Installation
Phorg uses PIL for reading photo exif tags.
It also needs pyprind to display copying progression.

#Usage

    usage: phorg.py [-h] [-r] [-d] [-c] [-v] [-s] [-t] [-o] [-m MONTHS] [-y YEAR]
                    src_dir dest_dir

    A simple photo organizer

    positional arguments:
      src_dir               photo directory
      dest_dir              target directory

    optional arguments:
      -h, --help            show this help message and exit
      -r, --recursive       process sub-directories
      -d, --dry             dry run
      -c, --copy            copy photos instead of moving
      -v, --video           handle videos
      -s, --separate        handle videos and photos separately
      -t, --use-ctime       use file created time if neither exif information nor
                            file name can reveal the photo taken time
      -o, --overwrite       overwriting existing files
      -m MONTHS, --months MONTHS
                            a string of namesseparated by commas that be used as
                            month directories,or 'system' (default) for using
                            system month names,or 'number' for using month number
                            as names,
      -y YEAR, --year-prefix YEAR
                            prefix for year directory
