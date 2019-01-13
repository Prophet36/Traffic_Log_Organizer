import csv


class FileReader:

    @staticmethod
    def get_file_data(filename):
        with open(filename) as file:
            data = csv.reader(file)
            output = list()
            for row in data:
                output.append(row[0])
            return output


class FileWriter:

    @staticmethod
    def write_data_as_csv(data, filename):
        with open(filename, 'w+') as file:
            for line in data:
                for item in line:
                    file.write(item)
                    file.write(";")
                file.write("\n")


if __name__ == "__main__":
    FileReader.get_file_data("../data/log_original.csv")
