import argparse
import os
import shutil
from PIL import Image
#from PIL.ExifTags import TAGS

from datetime import datetime
import re

class PhorgError(Exception):
    def __init__(self, msg):
        self.__message = msg
    def __str__(self):
        return repr(self.__message)

class Phorg:
    FILE_PHOTO = 0
    FILE_VIDEO = 1
    FILE_PHOTO_ERROR = 2
    FILE_VIDEO_ERRO = 3
    FILE_ERROR = -1

    IMAGE_EXTS = ['.jpg', '.gif', '.tiff', '.png']
    VIDEO_EXTS = ['.mp4', '.mov', '.3gp']
    DATETIME_PATTERNS =[
        ('[0-9]{4}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}','%Y%m%d%H%M%S'),
    ]
    def __init__(self, args):
        self.__args = args
        self.__file_list = []
        self.__photo_dir = None
        self.__video_dir = None
        self.__perror_dir = None
        self.__verror_dir = None

    def __handle_file(self, afile):
        file_path = os.path.abspath(afile)
        file_name = os.path.split(file_path)[-1]
        file_ext = os.path.splitext(file_name)[-1].lower()
        #print afile
        if file_ext in Phorg.IMAGE_EXTS:
            self.__handle_image(afile)
        elif self.__args.video and file_ext in Phorg.VIDEO_EXTS:
            self.__handle_video(afile)
        else:
            self.__handle_unexpected_file(afile, Phorg.FILE_ERROR)

    def __get_datetime_from_file_name(self, file_name):
        for p1, p2 in Phorg.DATETIME_PATTERNS:
            try:
                m = re.search(p1, file_name)
                if m:
                    ts = []
                    for c in m.group(0):
                        if c not in ' -_.:':
                            ts.append(c)
                    t = datetime.strptime(''.join(ts)[0:14], p2)
                    if t:
                        return t
            except:
                pass
    def __get_datetime_from_file_attributes(self, afile):
        if self.__args.ctime:
            return datetime.fromtimestamp(os.path.getctime(afile))

    def __get_datetime_from_exif(self, img_file):
        try:
            i = Image.open(img_file)
            ts = i._getexif().get(0x9003, '')
            try:
                return datetime.strptime(ts,"%Y:%m:%d %H:%M:%S")
            except:
                pass
        except:
            pass

    def __get_year(self, time):
        return str(time.year)

    def __get_month(self, time):
        return str(time.month)

    def __handle_unexpected_file(self, afile, file_type):
        if file_type == Phorg.FILE_ERROR:
            print afile, "is not is not processed"
        else:
            self.__to_dest(afile, file_type, None)

    def __handle_image(self, img_file):
        t = None
        t = self.__get_datetime_from_exif(img_file)
        if not t:
            t = self.__get_datetime_from_file_name(img_file)
        if not t:
            t = self.__get_datetime_from_file_attributes(img_file)
        if t:
            self.__to_dest(img_file, Phorg.FILE_PHOTO, t)
        else:
            self.__handle_unexpected_file(img_file, Phorg.FILE_PHOTO_ERROR)

    def __handle_video(self, video_file):
        t = None
        t = self.__get_datetime_from_file_name(video_file)
        if not t:
            t = self.__get_datetime_from_file_attributes(video_file)
        if t:
            self.__to_dest(video_file, Phorg.FILE_VIDEO, t)
        else:
            self.__handle_unexpected_file(video_file, Phorg.FILE_VIDEO_ERRO)

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
        self.__args.src_dir = os.path.abspath(self.__args.src_dir)
        self.__args.dest_dir = os.path.abspath(self.__args.dest_dir.rstrip('/\\'))

        if not os.path.isdir(self.__args.src_dir):
            raise PhorgError("{} is not a directory".format(self.__args.src_dir))

        if os.path.commonprefix([self.__args.src_dir, self.__args.dest_dir]) == self.__args.src_dir:
            raise PhorgError("{} is a subfolder of the source".format(self.__args.dest_dir))

    def __create_dest_dir(self):
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
            if self.__args.separate and not os.path.exists(self.__verror_dir):
                os.makedirs(self.__verror_dir)
        except Exception as e:
            raise PhorgError(str(e))

    def process(self):
        self.__check_dirs()
        self.__create_dest_dir()
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

def main():
    parser = argparse.ArgumentParser(description="A simple photo organizer")
    parser.add_argument("src_dir", help="photo directory")
    parser.add_argument("dest_dir", help="target directory")
    parser.add_argument("-r", "--recursive", action="store_true", dest="recursive", help="process folders recursively")
    parser.add_argument("-v", "--verbose", help="increase verbosity", action="store_true")
    parser.add_argument("-d", "--dry", dest="dry", action="store_true", help="dry run")
    parser.add_argument("-c", "--copy", dest="copy", help="copy photos instead of moving", action="store_true")
    parser.add_argument("-w", "--video", dest="video", help="handle videos", action="store_true")
    parser.add_argument("-s", "--separate", dest="separate", help="handle videos separately", action="store_true")
    parser.add_argument("-t", "--use-ctime", dest="ctime", help="use file created time", action="store_true")
    args = parser.parse_args()

    try:
        phorg = Phorg(args)
        phorg.process()
    except PhorgError as e:
        print e

if __name__ == "__main__" : main()


