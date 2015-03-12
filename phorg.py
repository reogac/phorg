import os
from gi.repository import GExiv2
def process(folder_name):
    file_list = [folder_name]

    while len(file_list) > 0 :
        current_file = file_list.pop()
        if os.path.isdir(current_file) :
            for file_name in os.listdir(current_file) :
                file_list.append(os.path.join(current_file, file_name))
        if os.path.isfile(current_file) :
            process_file(current_file)

def process_file(file_name) :
    print file_name

process("/home/tungtq/projects/bun")
