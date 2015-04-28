# phorg - a simple photo organizer

Phorg is a simple command line tool for organizing your photos into year/month folders.

First it reads exif metadata to find the photo taken time. If the information is not available, it try to search in file name (onedrive, dropbox camera upload apps normally have this timestamp in file names). If neither methods work, it can optionally take the file created time as the timestamp.

Photos/videos with known timestamp are put in year/month folders. Month names can be defined with '-m MONTHS' option.

#Installation
Phorg uses PIL for reading photo exif tags.
It also needs pyprind to display copying progression. pyprind in turn need psutil

    sudo pip install PIL
    
    sudo pip install psutil
    
    sudo pip install pyprind

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
                            a string of names separated by commas that be used as
                            month directories,or 'system' (default) for using
                            system month names,or 'number' for using month number
                            as names,
      -y YEAR, --year-prefix YEAR
                            prefix for year directory
