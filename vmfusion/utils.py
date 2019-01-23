import os


def file_must_exist(file_type, file):
    if not os.path.isfile(file):
        raise ValueError("{0} at path {1} does not exist".format(file_type, file))


def file_must_not_exist(file_type, file):
    if os.path.isfile(file):
        raise ValueError("{0} at path {1} already exists".format(file_type, file))


def get_abspath(path):
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    return path
