import os
from datetime import datetime
from gi.repository.GExiv2 import Metadata

class PhotoData(object):
    IMAGE_EXTS = ['.jpg', '.gif', '.tiff', '.png']

    def __init__(self):
        self.__file_path = ""
        self.__file_name = ""
        self.__file_size = 0
        self.__datetime = None
        self.__camera = "unknown"

    def read_photo(self, file_path):
        self.__file_path = os.path.abspath(file_path)
        self.__file_name, ext = os.path.split(self.__file_path)
        self.__file_size = os.path.get_size(self.__file_path)
        if ext in PhotoData.IMAGE_EXTS:
            self.__get_date_time()
    def __get_date_time(self):
        exif = Metadata(self.__file_path)
        if exif.has_tag("Exif.Image.DateTime"):
            time_str = exif.get_tag_string("Exif.Image.DateTime")
        elif exif.has_tag("Exif.Photo.DataTiimeOriginal"):
            time_str = exif.get_tag_string("Exif.Photo.DateTimeOriginal")

        self.__datetime = datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")

class Phorg :
    PHOTO_EXTS = ['.jpg', '.gif', '.png', '.tiff']
    def __init__(self):
        self.input_dir = "."
        self.output_dir = "outputs"
        self.auto_rename = True
        self.grouping = True
        self.file_dict = {}

    def readArgs(self, args) :
        self.auto_rename = True

    def process(self):
        self.__create_output_dir()
        file_list = [self.input_dir]
        while len(self.file_list) > 0 :
            current_file = file_list.pop()
            if os.path.isdir(current_file) :
                for file_path in os.listdir(current_file) :
                    file_list.append(os.path.join(current_file, file_path))
            if os.path.isfile(current_file) :
                self.__process_file(current_file)
        if (self.grouping) :
            self.__group()
        print self.file_dict

    def __process_file(self, file_path) :
        if self.__is_photo(file_path) :
            self.__process_photo(file_path)

    def __process_photo(self, file_path) :
        exif = Metadata(file_path)
        if exif.has_tag("Exif.Image.DateTime"):
            time_str = exif.get_tag_string("Exif.Image.DateTime")
        elif exif.has_tag("Exif.Photo.DataTiimeOriginal"):
            time_str = exif.get_tag_string("Exif.Photo.DateTimeOriginal")

        created_time = datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")
        self.file_dict[created_time] = file_path
        #print exif.get_tags()

    def __is_photo(self, file_path):
        name, ext = os.path.splitext(file_path)
        if ext in Phorg.PHOTO_EXTS :
            return True
        return False
    def __create_output_dir(self) :
        if not os.path.exists(self.output_dir) :
            os.makedirs(self.output_dir)
    def __group(self) :
        print "Do grouping"

myphorg= Phorg()
#myphorg.process("/home/tungtq/projects/bun")
myphorg.process()
