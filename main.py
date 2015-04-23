import argparse
import os
"""import datetime
import re
"""
class Phorg:
    IMAGE_EXTS = ['.jpg', '.gif', '.tiff', '.png']
    def __init__(self, args):
        self.__args = args
        self.__file_list = []
    def __process_file(self, afile):
        file_path = os.path.abspath(afile)
        file_name = os.path.split(file_path)[-1]
        file_ext = os.path.splitext(file_name)[-1]
        if file_ext not in Phorg.IMAGE_EXTS:
            return self.__process_unexpected_file(afile)
        print file_name, file_ext
    def __process_unexpected_file(self, afile):
        print afile, "is not a photo"
    def process(self):
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
    parser.add_argument("-r", "--recursive", action="store_true", dest="recursive", default=False, help="process folders recursively")
    parser.add_argument("-v", "--verbose", help="increase verbosity", action="store_true")
    parser.add_argument("-d", "--dry", dest="dry", action="store_true", help="dry run")
    parser.add_argument("-c", "--copy", dest="copy", help="copy photos instead of moving", action="store_true")
    args = parser.parse_args()

    print "source folder = ", args.src_dir
    print "target folder = ", args.dest_dir
    print "is recursive = ", args.recursive
    print "is verbose = ", args.verbose
    print "is dry run = ", args.dry
    phorg = Phorg(args)
    phorg.process()


if __name__ == "__main__" : main()


