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
    def __str__(self):
        return self.__datetime.strftime("%Y-%m-%d_%H:%M:%S")
    @property
    def datetime(self):
        """get the time when the photo was created"""
        return self.__datetime

    def read_photo(self, file_path):
        self.__file_path = os.path.abspath(file_path)
        self.__file_name = os.path.split(self.__file_path)[1]
        ext = os.path.splitext(self.__file_name)[1]
        self.__file_size = os.path.getsize(self.__file_path)

        if not ext in PhotoData.IMAGE_EXTS:
            return False
        if not self.__get_datetime_from_exif():
            return self.__get_datetime_from_name()
        else:
            return True

    def __get_datetime_from_exif(self):
        try:
            exif = Metadata(self.__file_path)
            time_str = exif.get_tag_string("Exif.Image.DateTime")
            if len(time_str) == 0:
                time_str = exif.get_tag("Exif.Photo.DataTiimeOriginal")
            self.__datetime = datetime.strptime(time_str, "%Y:%m:%d %H:%M:%S")
            return True
        except:
            return False
    def __get_datetime_from_name(self):
        print "Trying to get datetime from %s" % self.__file_name
        return False

class Phorg :
    def __init__(self):
        self.__input_dir = "."
        self.__output_dir = "outputs"
        self.__auto_rename = True
        self.__grouping = True
        self.__file_dict = {}

    def readArgs(self, args) :
        self.__auto_rename = True

    def process(self):
        self.__create_output_dir()
        file_list = [self.__input_dir]
        while len(file_list) > 0 :
            current_file = file_list.pop()
            if os.path.isdir(current_file) :
                for file_path in os.listdir(current_file) :
                    file_list.append(os.path.join(current_file, file_path))
            elif os.path.isfile(current_file) :
                self.__process_file(current_file)
        if (self.__grouping) :
            self.__group()
        print self.__file_dict

    def __process_file(self, file_path):
        photo = PhotoData()
        if photo.read_photo(file_path):
            self.__file_dict[photo.datetime] = photo

    def __create_output_dir(self) :
        if not os.path.exists(self.__output_dir) :
            os.makedirs(self.__output_dir)

    def __group(self) :
        print "Do grouping"

myphorg= Phorg()
#myphorg.process("/home/tungtq/projects/bun")
myphorg.process()
