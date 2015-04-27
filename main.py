import argparse
import os
import shutil
from PIL import Image
#from PIL.ExifTags import TAGS

from datetime import datetime
import re

FILE_PHOTO = 0
FILE_VIDEO = 1
FILE_PHOTO_ERROR = 2
FILE_VIDEO_ERRO = 3

IMAGE_EXTS = ['.jpg', '.gif', '.tiff', '.png']
VIDEO_EXTS = ['.mp4', '.mov', '.3gp']
DATETIME_PATTERNS =[
    ('[0-9]{4}[ -_.:]?[0-9]{2}[ -_.:]?\
     [0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?\
     [0-9]{2}[ -_.:]?[0-9]{2}'
     ,'%Y%m%d%H%M%S'),
]

_args = None
_file_list = []
_photo_dir = None
_video_dir = None
_perror_dir = None
_verror_dir = None
_newest_time = None

class PhorgError(Exception):
    def _init_(self, msg):
        self.__message = msg
    def _str_(self):
        return repr(self.__message)

def _get_time(s):
    """
    Returns datetime from a string
    """
    for p1, p2 in DATETIME_PATTERNS:
        m = re.search(p1, s)
        if m:
            ts = []
            for c in m.group(0):
                if c not in ' -_.:':
                    ts.append(c)
            return datetime.strptime(''.join(ts)[0:14], p2)


def _get_datetime_from_file_name(file_name):
    """
    Returns datetime from a file name
    """
    try:
        return _get_time(file_name)
    except:
        pass

def _get_datetime_from_file_attributes( afile):
    """
    Returns the created time by reading file attributes
    """

    if _args.ctime:
        return datetime.fromtimestamp(os.path.getctime(afile))

def _get_datetime_from_exif( img_file):
    """
    Returns photo taken time from EXIF meta data
    """

    try:
        i = Image.open(img_file)
        ts = i._getexif().get(0x9003, '')
        return datetime.strptime(ts,"%Y:%m:%d %H:%M:%S")
    except:
        pass

def _get_year( time):
    """
    Returns the year of a datetime input
    """
    return str(time.year)

def _get_month( time):
    """ Returns the month of a datetime input
    """

    return str(time.month)

def _get_image_time( img_file):
    t = None
    t = _get_datetime_from_exif(img_file)
    if not t:
        t = _get_datetime_from_file_name(img_file)
    if not t and _args.ctime:
        t = _get_datetime_from_file_attributes(img_file)
    return t

def _get_video_time( video_file):

    t = None
    t = _get_datetime_from_file_name(video_file)
    if not t and _args.ctime:
        t = _get_datetime_from_file_attributes(video_file)
    return t


def process():
    _check_dirs()
    _create_dest_dir()
    _collect_files()
    _process_files()

def _check_dirs():
    """
    Checks for the validity of the source and target directories
    """
    _args.src_dir = os.path.abspath(_args.src_dir)
    _args.dest_dir = os.path.abspath(_args.dest_dir.rstrip('/\\'))

    if not os.path.isdir(_args.src_dir):
        raise PhorgError("{} is not a directory".format(_args.src_dir))

    if os.path.commonprefix([_args.src_dir, _args.dest_dir]) == _args.src_dir:
        raise PhorgError("{} is a subfolder of the source".
                         format(_args.dest_dir))

def _create_dest_dir(self):
    """
    Creates the target directory and its subditectories
    """
    try:
        _photo_dir = _args.dest_dir
        _video_dir = _photo_dir
        if not os.path.exists(_photo_dir) :
            os.makedirs(_photo_dir)
            if _args.separate:
                _video_dir = _photo_dir + "/videos"
                _photo_dir = _photo_dir + "/photos"

            if not os.path.exists(_photo_dir) :
                os.makedirs(_photo_dir)
                if not os.path.exists(_video_dir) :
                    os.makedirs(_video_dir)
                    _perror_dir = _photo_dir + "/nodate"
                    _verror_dir = _video_dir + "/nodate"
                    if not os.path.exists(_perror_dir):
                        os.makedirs(_perror_dir)
                        if _args.separate\
                            and not os.path.exists(_verror_dir):
                            os.makedirs(_verror_dir)
    except Exception as e:
        raise PhorgError(str(e))

def _collect_files(self):
    """
    Collects files in source directory for moving/copying
    """

    dir_list = [_args.src_dir]
    _file_list = []
    while len(dir_list)>0:
        cur_dir = dir_list.pop()
        for afile in os.listdir(cur_dir):
            afile = os.path.join(cur_dir, afile)
            if os.path.isfile(afile):
                attributes = _read_file(afile)
                if attributes:
                    _file_list.append(attributes)
            elif _args.recursive and os.path.isdir(afile):
                dir_list.append(afile)

def _read_file( afile):
    file_path = os.path.abspath(afile)
    file_name = os.path.split(file_path)[-1]
    file_ext = os.path.splitext(file_name)[-1].lower()
    t = None
    file_type = None
    if file_ext in IMAGE_EXTS:
        t = _get_image_time(afile)
        file_type = FILE_PHOTO
    elif _args.video and file_ext in VIDEO_EXTS:
        t = _get_video_time(afile)
        file_type = FILE_VIDEO
    else:
        _handle_unexpected_file(afile)

    if not file_exists(afile, file_type, t):
        return (afile, t)

def _get_prefix(file_type, t):
    ret = None
    if file_type == FILE_PHOTO:
        if t:
            ret = _photo_dir
        else:
            ret = _perror_dir
    elif file_type == FILE_VIDEO:
        if t:
            ret = _video_dir
        else:
            ret = _verror_dir

    if t:
        year = _get_year(t)
        month = _get_month(t)
        ret = ret + '/' + year + '/' + month
    return ret

def file_exists(file_path, file_type, t):
    file_full_name = os.path.split(file_path)[-1]
    file_name,file_ext = os.path.splitext(file_full_name)
    dest_prefix = _get_prefix(file_type, t)
    dest_path = dest_prefix + '/' + file_full_name
    file_size = os.path.getsize(file_path)
    return os.path.exists(dest_path) and file_size==os.path.getsize(dest_path)

def _process_files():
    for afile, file_type, t in _file_list:
        _copy_file(afile, t, file_type)
    pass
def _copy_file(file_path, file_type, t):
    pass

def _handle_unexpected_file( afile):
    print afile, "is not is not processed"

def _to_dest( file_path, file_type, time):
    dest_prefix = None
    if file_type == FILE_PHOTO:
        dest_prefix = _photo_dir
    elif file_type == FILE_VIDEO:
        dest_prefix = _video_dir
    elif file_type == FILE_PHOTO_ERROR:
        dest_prefix = _perror_dir
    else:
        dest_prefix = _verror_dir
        if file_type in [FILE_PHOTO, FILE_VIDEO]:
            year = _get_year(time)
            month = _get_month(time)
            dest_prefix = dest_prefix + '/' + year
            if not os.path.exists(dest_prefix):
                os.makedirs(dest_prefix)
                dest_prefix = dest_prefix + '/' + month
                if not os.path.exists(dest_prefix):
                    os.makedirs(dest_prefix)

    file_full_name = os.path.split(file_path)[-1]
    file_name,file_ext = os.path.splitext(file_full_name)
    cnt = 1
    dest_path = dest_prefix + '/' + file_full_name
    while os.path.exists(dest_path):
        dest_path = dest_prefix + '/' + file_name + '(' + str(cnt) + ')' + file_ext
        cnt += 1
        if _args.dry:
            print 'copy {} to {}'.format(file_path, dest_path)
        elif _args.copy:
            shutil.copy(file_path, dest_path)
        else:
            os.rename(file_path, dest_path)

def main():
    parser = argparse.ArgumentParser(description="A simple photo organizer")
    parser.add_argument("src_dir", help="photo directory")
    parser.add_argument("dest_dir", help="target directory")
    parser.add_argument("-r", "--recursive", action="store_true",
                        dest="recursive", help="process folders recursively")
    parser.add_argument("--verbose", help="increase verbosity",
                        action="store_true")
    parser.add_argument("-d", "--dry", dest="dry", action="store_true",
                        help="dry run")
    parser.add_argument("-c", "--copy", dest="copy",
                        help="copy photos instead of moving",
                        action="store_true")
    parser.add_argument("-v", "--video", dest="video",
                        help="handle videos", action="store_true")
    parser.add_argument("-s", "--separate", dest="separate",
                        help="handle videos separately", action="store_true")
    parser.add_argument("-t", "--use-ctime", dest="ctime",
                        help="use file created time", action="store_true")
    parser.add_argument("-a", "--all", dest="all",
                        help="process all files, include old ones",
                        action="store_false")
    args = parser.parse_args()
    print args.newest
    try:
        process()
    except PhorgError as e:
        print e

if __name__ == "__main__" : main()

