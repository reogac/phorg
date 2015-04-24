import argparse
import os
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
    IMAGE_EXTS = ['.jpg', '.gif', '.tiff', '.png']
    VIDEO_EXTS = ['.mp4', '.mov', '.3gp']
    DATETIME_PATTERNS =[
        ('[0-9]{4}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}[ -_.:]?[0-9]{2}','%Y%m%d%H%M%S'),
    ]
    def __init__(self, args):
        self.__args = args
        self.__file_list = []

    def __process_file(self, afile):
        file_path = os.path.abspath(afile)
        file_name = os.path.split(file_path)[-1]
        file_ext = os.path.splitext(file_name)[-1].lower()
        print afile
        if file_ext in Phorg.IMAGE_EXTS:
            self.__handle_image(afile)
        elif file_ext in Phorg.VIDEO_EXTS:
            self.__handle_video(afile)
        else:
            self.__handle_unexpected_file(afile)

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

        except OSError as e:
            print e
            pass

    def __handle_unexpected_file(self, afile):
        print afile, "is not is not processed"

    def __handle_image(self, img_file):
        t = None
        t = self.__get_datetime_from_exif(img_file)
        if not t:
            t = self.__get_datetime_from_file_name(img_file)
        if not t:
            t = self.__get_datetime_from_file_attributes(img_file)
        if t:
            print t

    def __handle_video(self, video_file):
        t = None
        t = self.__get_datetime_from_file_name(video_file)
        if not t:
            t = self.__get_datetime_from_file_attributes(video_file)
        if t:
            print t


    def process(self):
        self.__args.src_dir = os.path.abspath(self.__args.src_dir)
        self.__args.dest_dir = os.path.abspath(self.__args.dest_dir.rstrip('/\\'))

        if not os.path.isdir(self.__args.src_dir):
            raise PhorgError("{} is not a directory".format(self.__args.src_dir))

        if os.path.commonprefix([self.__args.src_dir, self.__args.dest_dir]) == self.__args.src_dir:
            raise PhorgError("{} is a subfolder of the source".format(self.__args.dest_dir))

        if not os.path.exists(self.__args.dest_dir) :
            os.makedirs(self.__args.dest_dir)

        dir_list = [self.__args.src_dir]
        self.__file_list = []
        while len(dir_list)>0:
            cur_dir = dir_list.pop()
            for afile in os.listdir(cur_dir):
                afile = os.path.join(cur_dir, afile)
                if os.path.isfile(afile):
                    self.__process_file(afile)
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

    print "source folder = ", args.src_dir
    print "target folder = ", args.dest_dir
    print "is recursive = ", args.recursive
    print "is process videos = ", args.video
    print "is verbose = ", args.verbose
    print "is dry run = ", args.dry
    try:
        phorg = Phorg(args)
        phorg.process()
    except PhorgError as e:
        print e

if __name__ == "__main__" : main()


