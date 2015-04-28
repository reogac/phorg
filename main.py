import argparse
import calendar
import os
import shutil
import re
import pyprind
from PIL import Image
from datetime import datetime

FILE_PHOTO = 0
FILE_VIDEO = 1

IMAGE_EXTS = ['.jpg', '.gif', '.tiff', '.png']
VIDEO_EXTS = ['.mp4', '.mov', '.3gp']

DATETIME_PATTERNS =[
    ('[0-9]{4}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?'
     '[0-9]{2}[ -_.:]?[0-9]{2}',
     '%Y%m%d%H%M%S'),
]

args = None
file_list = []
photo_dir = None
video_dir = None
perror_dir = None
verror_dir = None

class PhorgError(Exception):
    def _init_(self, msg):
        self.__message = msg
    def _str_(self):
        return repr(self.__message)


def get_datetime_from_file_name(file_name):
    """
    Returns datetime from a file name
    """
    try:
        for p1, p2 in DATETIME_PATTERNS:
            m = re.search(p1, file_name)
            if m:
                ts = []
                for c in m.group(0):
                    if c not in ' -_.:':
                        ts.append(c)
                return datetime.strptime(''.join(ts)[0:14], p2)
    except:
        pass

def get_datetime_from_file_attributes(afile):
    """
    Returns the created time by reading file attributes
    """

    if args.ctime:
        return datetime.fromtimestamp(os.path.getctime(afile))

def get_datetime_from_exif(img_file):
    """
    Returns photo taken time from EXIF meta data
    """
    try:
        i = Image.open(img_file)
        ts = i._getexif().get(0x9003, '')
        return datetime.strptime(ts,"%Y:%m:%d %H:%M:%S")
    except:
        pass

def get_year(time):
    """
    Returns the year from a datetime object
    """
    if args.year:
        return args.year + ' ' + str(time.year)
    return str(time.year)

def get_month(time):
    """
    Returns the month of a datetime input
    """
    return args.months[time.month-1]

def get_image_time(img_file):
    t = None
    t = get_datetime_from_exif(img_file)
    if not t:
        t = get_datetime_from_file_name(img_file)
    if not t and args.ctime:
        t = get_datetime_from_file_attributes(img_file)
    return t

def get_video_time(video_file):
    t = None
    t = get_datetime_from_file_name(video_file)
    if not t and args.ctime:
        t = get_datetime_from_file_attributes(video_file)
    return t


def process():
    check_dirs()
    create_dest_dir()
    collect_files()
    process_files()

def check_dirs():
    """
    Checks for the validity of the source and target directories
    """
    args.src_dir = os.path.abspath(args.src_dir)
    args.dest_dir = os.path.abspath(args.dest_dir.rstrip('/\\'))

    if not os.path.isdir(args.src_dir):
        raise PhorgError("{} is not a directory".format(args.src_dir))

    if os.path.commonprefix([args.src_dir, args.dest_dir]) == args.src_dir:
        raise PhorgError("{} is a subfolder of the source".
                         format(args.dest_dir))

def create_dest_dir():
    """
    Creates the target directory and its subditectories
    """
    global photo_dir, video_dir, perror_dir, verror_dir
    try:
        photo_dir = args.dest_dir
        video_dir = photo_dir
        if not os.path.exists(photo_dir) :
            os.makedirs(photo_dir)
        if args.separate:
            video_dir = photo_dir + "/videos"
            photo_dir = photo_dir + "/photos"

        if not os.path.exists(photo_dir) :
            os.makedirs(photo_dir)
        if not os.path.exists(video_dir) :
            os.makedirs(video_dir)

        perror_dir = photo_dir + "/nodate"
        verror_dir = video_dir + "/nodate"
        if not os.path.exists(perror_dir):
            os.makedirs(perror_dir)
        if args.separate and not os.path.exists(verror_dir):
            os.makedirs(verror_dir)
    except Exception as e:
        raise PhorgError(str(e))

def collect_files():
    """
    Collects files in source directory for moving/copying
    """
    global file_list
    dir_list = [args.src_dir]
    file_list = []
    while len(dir_list)>0:
        cur_dir = dir_list.pop()
        for afile in os.listdir(cur_dir):
            afile = os.path.join(cur_dir, afile)
            if os.path.isfile(afile):
                attributes = read_file(afile)
                if attributes:
                    file_list.append(attributes)
            elif args.recursive and os.path.isdir(afile):
                dir_list.append(afile)

def read_file(afile):
    file_path = os.path.abspath(afile)
    file_name = os.path.split(file_path)[-1]
    file_ext = os.path.splitext(file_name)[-1].lower()
    t = None
    file_type = None
    if file_ext in IMAGE_EXTS:
        t = get_image_time(afile)
        file_type = FILE_PHOTO
    elif args.video and file_ext in VIDEO_EXTS:
        t = get_video_time(afile)
        file_type = FILE_VIDEO
    else:
        handle_unexpected_file(afile)
        return
    if args.overwrite:
        return (afile, file_type, t)

    file_size = os.path.getsize(file_path)
    dest_prefix = get_prefix(file_type, t)
    if t:
        dest_prefix = dest_prefix + '/' + get_year(t) + '/' + get_month(t)

    if not file_exists(dest_prefix, file_name, file_size):
        return (afile, file_type, t)

def get_prefix(file_type, t):
    ret = None
    if file_type == FILE_PHOTO:
        if t:
            ret = photo_dir
        else:
            ret = perror_dir
    elif file_type == FILE_VIDEO:
        if t:
            ret = video_dir
        else:
            ret = verror_dir

    return ret

def file_exists(prefix_path, file_name, file_size):
    dest_path = prefix_path + '/' + file_name
    return os.path.exists(dest_path) and file_size==os.path.getsize(dest_path)

def process_files():
    n = len(file_list)
    if n==0:
        print "Nothing to process"
        return
    if not args.dry:
        title = "Moving files"
        if args.copy:
            title = "Copying files"
        bar = pyprind.ProgBar(n, monitor=True, title=title)
    for i in range(n):
        afile, file_type, t = file_list[i]
        copy_file(afile, file_type, t)
        if not args.dry:
            bar.update()

def copy_file(file_path, file_type, t):
    dest_prefix = get_prefix(file_type, t)
    file_full_name = os.path.split(file_path)[-1]
    file_name,file_ext = os.path.splitext(file_full_name)
    file_size = os.path.getsize(file_path)
    dest_ext = ""
    if t:
        year = get_year(t)
        month = get_month(t)
        dest_ext = '/' + year + '/' + month

    cnt = 1
    if not args.overwrite:
        while file_exists(dest_prefix + dest_ext,
                          file_full_name,
                          file_size):
            file_full_name = file_name + '(' + str(cnt) + ')' + file_ext
            cnt += 1

    dest_path = dest_prefix
    if t:
        dest_path = dest_prefix + '/' + year
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        dest_path = dest_path + '/' + month
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

    dest_path = dest_path + '/' + file_full_name

    if args.dry:
        print 'copy {} to {}'.format(file_path, dest_path)
    elif args.copy:
        shutil.copy(file_path, dest_path)
    else:
        os.rename(file_path, dest_path)

def handle_unexpected_file(afile):
    if args.verbose:
        print afile, "is not is not processed"

def get_months(s):
    ret = s.split(",")
    if len(ret) == 1:
        if ret[0].lower() == "system":
            return get_system_months()
        if ret[0].lower() == "number":
            return get_number_months()
    if len(ret) != 12:
        raise PhorgError("We needs exactly 12 months")
    return ret

def get_system_months():
    ret = []
    for i in range(1,13):
        ret.append(calendar.month_name[i])
    return ret
def get_number_months():
    ret =[]
    for i in range(1,13):
        ret.append(str(i))
    return ret

def main():
    global args
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
    parser.add_argument("-o", "--overwrite", dest="overwrite",
                        help="overwriting existing files", action="store_true")

    parser.add_argument("-m", "--months", dest="months", help="a string of names"
                        "separated by spaces that be used as month directories,"
                        "or \'system\' for using system month names,"
                        "or \'number\' for using month number as names, ",
                       type=get_months, default="system")
    parser.add_argument("-y", "--year-prefix",
                        help="prefix for name of year directory", dest="year")

    args = parser.parse_args()
    try:
        process()
    except PhorgError as e:
        print e

if __name__ == "__main__" : main()

