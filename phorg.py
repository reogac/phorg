import os
from gi.repository import GExiv2


class Phorg :
    photo_exts = ['.jpg', '.gif', '.png', '.tiff']
    def __init__(self):
        self.input_dir = "."
        self.output_dir = "outputs"
        self.auto_rotate = True
        self.auto_rename = True
        self.grouping = True
        self.file_list = []

    def readArgs(self, args) :
        self.auto_rename = False

    def process(self):
        self.file_list = [self.input_dir]
        while len(self.file_list) > 0 :
            current_file = self.file_list.pop()
            if os.path.isdir(current_file) :
                for file_name in os.listdir(current_file) :
                    self.file_list.append(os.path.join(current_file, file_name))
            if os.path.isfile(current_file) :
                self.process_file(current_file)

    def process_file(self, file_name) :
        if self.is_photo(file_name) :
            self.process_photo(file_name)

    def process_photo(self, filename) :

        return True;

    def is_photo(self, file_name):
        name, ext = os.path.splitext(file_name)
        if ext in Phorg.photo_exts :
            return True
        return False

myphorg= Phorg()
#myphorg.process("/home/tungtq/projects/bun")
myphorg.process()i
