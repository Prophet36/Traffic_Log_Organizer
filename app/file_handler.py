import errno
import os


class FileHandler:

    @staticmethod
    def get_data_from_file(filename):
        with open(filename, "r") as file:
            data = file.read().splitlines()
            return data

    @staticmethod
    def write_data_to_file(data, filename):
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        with open(filename, 'w') as file:
            for line in data:
                file.write(line)
                file.write("\n")
