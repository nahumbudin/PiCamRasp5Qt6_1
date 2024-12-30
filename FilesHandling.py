import ctypes
import multiprocessing
from datetime import datetime
from pathlib import Path
import os

import globals
from ConfigurationManager import ConfigurationManager


def get_today_date_string():
    now = datetime.now()
    today_string = now.strftime("%Y_%m_%d")
    return today_string


def seek_directory(path=globals.DEFAULT_IMAGES_DIR, dir_name=""):
    p = Path(path + dir_name)
    dir_exists = p.exists()
    return dir_exists


def create_directory(path=globals.DEFAULT_IMAGES_DIR, dir_name=""):
    full_path = path + dir_name
    os.mkdir(full_path)


def get_next_image_path_and_name(captured_images_files_directory,
                                 captured_images_file_name,
                                 captured_images_file_extension):
    """ This function returns the next file name (and creates a new directory each day) """
    # This configuration manager instance handles only the incremental file name indexes
    configuration_manager = ConfigurationManager(globals.DEFAULT_FILES_INDEX_CONFIGURATION_FILE)
    image_index = configuration_manager.get_next_image_file_index()

    # sub_dir = get_today_date_string()
    active_images_dir = captured_images_files_directory  # + sub_dir
    # if not seek_directory(path=captured_images_files_directory, dir_name=sub_dir):
    #     create_directory(path=captured_images_files_directory, dir_name=sub_dir)
    # File name = image_current date_running index
    pic_file_full_path = (active_images_dir + '/' + captured_images_file_name +
                          '_' + get_today_date_string() + '_' +
                          image_index + captured_images_file_extension)

    return pic_file_full_path


class FilesHandling:
    def __init__(self):
        self.last_browsed_image_full_path = globals.DEFAULT_IMAGES_DIR
        self.last_selected_image_file = ""
        self.active_images_dir = globals.DEFAULT_IMAGES_DIR

    def set_last_browsed_file_full_path(self, full_path):
        self. last_browsed_image_full_path = full_path

    def get_last_browsed_file_full_path(self):
        return self.last_browsed_image_full_path

    def set_last_selected_image_file(self, file):
        self.last_selected_image_file = file

    def get_last_selected_image_file(self):
        return self.last_selected_image_file

    def set_active_images_dir(self, dir):
        self.active_images_dir = dir

    def get_active_images_dir(self):
        return self.active_images_dir


if __name__ == "__main__":

    dir = get_today_date_string()
    path = globals.DEFAULT_IMAGES_DIR
    if not seek_directory(path=path, dir_name=dir):
        create_directory(path=path, dir_name=dir)

    active_images_dir = path + dir
    print(active_images_dir)
