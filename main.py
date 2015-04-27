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
FILE_ERROR = -1

IMAGE_EXTS = ['.jpg', '.gif', '.tiff', '.png']
VIDEO_EXTS = ['.mp4', '.mov', '.3gp']
DATETIME_PATTERNS =[
    ('[0-9]{4}[ -_.:]?[0-9]{2}[ -_.:]?\
     [0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?\
     [0-9]{2}[ -_.:]?[0-9]{2}'
     ,'%Y%m%d%H%M%S'),
]

def get_time(s):
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

class PhorgError(Exception):
    def __init__(self, msg):
        self.__message = msg
        def __str__(self):
            return repr(self.__message)

class Phorg:
    def __init__(self, args):
        self.__args = args
        self.__file_list = []
        self.__photo_dir = None
        self.__video_dir = None
        self.__perror_dir = None
        self.__verror_dir = None
        self.__newest_time = None

    def __get_datetime_from_file_name(self, file_name):
        """
        Returns datetime from a file name
        """
        try:
            return Phorg.get_time(file_name)
        except:
            pass

    def __get_datetime_from_file_attributes(self, afile):
        """
        Returns the created time by reading file attributes
        """

        if self.__args.ctime:
            return datetime.fromtimestamp(os.path.getctime(afile))

    def __get_datetime_from_exif(self, img_file):
        """
        Returns photo taken time from EXIF meta data
        """

        try:
            i = Image.open(img_file)
            ts = i._getexif().get(0x9003, '')
            return datetime.strptime(ts,"%Y:%m:%d %H:%M:%S")
        except:
            pass

    def __get_year(self, time):
        """
        Returns the year of a datetime input
        """
        return str(time.year)

    def __get_month(self, time):
        """ Returns the month of a datetime input
        """

        return str(time.month)


    def __read_file(self, afile):
        file_path = os.path.abspath(afile)
        file_name = os.path.split(file_path)[-1]
        file_ext = os.path.splitext(file_name)[-1].lower()
        t = None
        if file_ext in Phorg.IMAGE_EXTS:
            t = self.__get_image_time(afile)
        elif self.__args.video and file_ext in Phorg.VIDEO_EXTS:
            t = self.__get_video_time(afile)
        else:
            self.__handle_unexpected_file(afile, Phorg.FILE_ERROR)
        return t

    def __is_newer(self, afile):
        """
        Returns True if the file is a new one
        """
        if self.__newest_time:
            mtime = datetime.fromtimestamp(os.path.getmtime(afile))
            if mtime > self.__newest_time:
                return True
        return False

    def __handle_unexpected_file(self, afile):
            print afile, "is not is not processed"

    def __get_image_time(self, img_file):
        if not self.__is_newer(img_file):
            return
        t = None
        t = self.__get_datetime_from_exif(img_file)
        if not t:
            t = self.__get_datetime_from_file_name(img_file)
        if not t and self.__args.ctime:
            t = self.__get_datetime_from_file_attributes(img_file)
        return t

    def __get_video_time(self, video_file):
        if not self.__is_newer(video_file):
            return

        t = None
        t = self.__get_datetime_from_file_name(video_file)
        if not t and self.__args.ctime:
            t = self.__get_datetime_from_file_attributes(video_file)
        return t

    def __to_dest(self, file_path, file_type, time):
        dest_prefix = None
        if file_type == Phorg.FILE_PHOTO:
            dest_prefix = self.__photo_dir
        elif file_type == Phorg.FILE_VIDEO:
            dest_prefix = self.__video_dir
        elif file_type == Phorg.FILE_PHOTO_ERROR:
            dest_prefix = self.__perror_dir
        else:
            dest_prefix = self.__verror_dir
            if file_type in [Phorg.FILE_PHOTO, Phorg.FILE_VIDEO]:
                year = self.__get_year(time)
                month = self.__get_month(time)
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
            if self.__args.dry:
                print 'copy {} to {}'.format(file_path, dest_path)
            elif self.__args.copy:
                shutil.copy(file_path, dest_path)
            else:
                os.rename(file_path, dest_path)

    def __check_dirs(self):
        """
        Checks for the validity of the source and target directories
        """
        self.__args.src_dir = os.path.abspath(self.__args.src_dir)
        self.__args.dest_dir = os.path.abspath(self.__args.dest_dir.
                                               rstrip('/\\'))

        if not os.path.isdir(self.__args.src_dir):
            raise PhorgError("{} is not a directory".
                             format(self.__args.src_dir))

        if os.path.commonprefix([self.__args.src_dir,
                                 self.__args.dest_dir]) == self.__args.src_dir:
            raise PhorgError("{} is a subfolder of the source".
                             format(self.__args.dest_dir))

    def __create_dest_dir(self):
        """
        Creates the target directory and its subditectories
        """
        try:
            self.__photo_dir = self.__args.dest_dir
            self.__video_dir = self.__photo_dir
            if not os.path.exists(self.__photo_dir) :
                os.makedirs(self.__photo_dir)
                if self.__args.separate:
                    self.__video_dir = self.__photo_dir + "/videos"
                    self.__photo_dir = self.__photo_dir + "/photos"

                if not os.path.exists(self.__photo_dir) :
                    os.makedirs(self.__photo_dir)
                    if not os.path.exists(self.__video_dir) :
                        os.makedirs(self.__video_dir)
                        self.__perror_dir = self.__photo_dir + "/nodate"
                        self.__verror_dir = self.__video_dir + "/nodate"
                        if not os.path.exists(self.__perror_dir):
                            os.makedirs(self.__perror_dir)
                            if self.__args.separate\
                                and not os.path.exists(self.__verror_dir):
                                os.makedirs(self.__verror_dir)
        except Exception as e:
            raise PhorgError(str(e))
    def __get_newest(self):
        pass
    def process(self):
        self.__check_dirs()
        self.__create_dest_dir()
        self.__get_newest()
        self.__collect_files()
        self.__process_files()

        dir_list = [self.__args.src_dir]
        self.__file_list = []
        while len(dir_list)>0:
            cur_dir = dir_list.pop()
            for afile in os.listdir(cur_dir):
                afile = os.path.join(cur_dir, afile)
                if os.path.isfile(afile):
                    self.__handle_file(afile)
                elif self.__args.recursive and os.path.isdir(afile):
                    dir_list.append(afile)
    def __collect_files(self):
        """
        Collects files in source directory for moving/copying
        """

        dir_list = [self.__args.src_dir]
        self.__file_list = []
        while len(dir_list)>0:
            cur_dir = dir_list.pop()
            for afile in os.listdir(cur_dir):
                afile = os.path.join(cur_dir, afile)
                if os.path.isfile(afile):
                    attributes = self.__read_file(afile)
                    if attributes:
                        self.__file_list.append(attributes)
                elif self.__args.recursive and os.path.isdir(afile):
                    dir_list.append(afile)

def parse_time(s):
    try:
        t = get_time(s)
        if t:
            return t
        else:
            raise argparse.ArgumentTypeError("Invalid datetime format")
    except Exception as e:
        raise argparse.ArgumentTypeError(str(e))

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
    parser.add_argument("--newer-than", dest="newest",
                        help="only process files whose modified time\
                        is newer than this"
                        , nargs=1, type=parse_time)
    parser.add_argument("-a", "--all", dest="all",
                        help="process all files, include old ones",
                        action="store_false")
    args = parser.parse_args()
    print args.newest
    try:
        phorg = Phorg(args)
        phorg.process()
    except PhorgError as e:
        print e

if __name__ == "__main__" : main()

