class FileReader:

    @staticmethod
    def get_file_data(filename):
        with open(filename, "r") as file:
            data = file.read().splitlines()
            return data


class FileWriter:

    @staticmethod
    def write_data_as_csv(data, filename):
        with open(filename, 'w') as file:
            for line in data:
                for idx, item in enumerate(line, start=1):
                    file.write(str(item))
                    if idx < len(line):
                        file.write(";")
                    else:
                        file.write("\n")
