import os

from app.data_handler import DataHandler
from app.file_handler import FileHandler


class ImpulseCalculator:

    def __init__(self):
        self._files = list()
        self._time_interval = 0
        self._impulse_data = None

    def calculate_impulses_in_directory(self, file_path):
        self._get_file_names_from_path(file_path=file_path)
        self._calculate_impulses_for_files()

    def parse_impulse_data_in_directory(self, file_path):
        self._get_file_names_from_path(file_path=file_path, find_impulses=True)
        self._parse_impulse_data_for_files()

    def _get_file_names_from_path(self, file_path, find_impulses=False):
        self._files.clear()
        if not find_impulses:
            for file in os.listdir(file_path):
                if not file.endswith("impulse.csv") and not file.endswith("impulses.csv"):
                    self._files.append(file_path + "/" + str(file))
        else:
            for file in os.listdir(file_path):
                if file.endswith("impulse.csv") and not file.endswith("total_impulses.csv"):
                    self._files.append(file_path + "/" + str(file))
            self._files.sort(key=lambda x: int(x.rsplit(sep="_", maxsplit=2)[-2]))

    def _calculate_impulses_for_files(self):
        if len(self._files) > 0:
            for file in self._files:
                self._calculate_impulses(file=file)
        else:
            print("No files in directory. Exiting program.")
            exit(1)

    def _calculate_impulses(self, file):
        data = FileHandler.get_data_from_file(file)
        data = [line.split(";") for line in data]
        data = [[DataHandler.convert_to_float(value=item) for item in line] for line in data]
        data = [[DataHandler.convert_to_int(value=item) for item in line] for line in data]
        self._time_interval = data[1][0] - data[0][0]
        if "Average" not in data[-3][0]:
            print("No average values present to calculate from. Exiting program.")
            exit(1)
        incoming_impulse_threshold = data[-4][1]
        outgoing_impulse_threshold = data[-4][2]
        impulses = self._get_impulses(data=data, inc_impulse=incoming_impulse_threshold,
                                      out_impulse=outgoing_impulse_threshold)
        number_of_impulses = self._calculate_number_of_impulses(impulses=impulses)
        average_impulse_time = self._calculate_average_impulse_time(impulses=impulses,
                                                                    number_of_impulses=number_of_impulses)
        self._add_impulse_data(impulses=impulses, number=number_of_impulses, avg_time=average_impulse_time)
        self._create_impulse_data_file(filename=str(file))

    def _get_impulses(self, data, inc_impulse, out_impulse):
        incoming_impulses = list()
        outgoing_impulses = list()
        new_inc_impulse = True
        new_out_impulse = True
        for line in data:
            if isinstance(line[0], str):
                continue
            if line[1] > inc_impulse:
                if new_inc_impulse:
                    incoming_impulses.append(["impulse start"])
                    new_inc_impulse = False
                impulse = [line[0], line[1]]
                incoming_impulses.append(impulse)
            else:
                new_inc_impulse = True
            if line[2] > out_impulse:
                if new_out_impulse:
                    outgoing_impulses.append(["impulse start"])
                    new_out_impulse = False
                impulse = [line[0], line[2]]
                outgoing_impulses.append(impulse)
            else:
                new_out_impulse = True
        return incoming_impulses, outgoing_impulses

    def _calculate_number_of_impulses(self, impulses):
        incoming_impulses = impulses[0]
        outgoing_impulses = impulses[1]
        number_of_incoming_impulses = 0
        number_of_outgoing_impulses = 0
        for item in incoming_impulses:
            if isinstance(item[0], str) and "start" in item[0]:
                number_of_incoming_impulses += 1
        for item in outgoing_impulses:
            if isinstance(item[0], str) and "start" in item[0]:
                number_of_outgoing_impulses += 1
        return number_of_incoming_impulses, number_of_outgoing_impulses

    def _calculate_average_impulse_time(self, impulses, number_of_impulses):
        inc_impulses = 1 if number_of_impulses[0] == 0 else number_of_impulses[0]
        out_impulses = 1 if number_of_impulses[1] == 0 else number_of_impulses[1]
        total_time = 0
        for item in impulses[0]:
            if "start" not in item:
                total_time += self._time_interval
        average_incoming_impulse_time = total_time / inc_impulses
        total_time = 0
        for item in impulses[1]:
            if "start" not in item:
                total_time += self._time_interval
        average_outgoing_impulse_time = total_time / out_impulses
        return average_incoming_impulse_time, average_outgoing_impulse_time

    def _add_impulse_data(self, impulses, number, avg_time):
        inc_number = ["Number of incoming impulses", number[0]]
        out_number = ["Number of outgoing impulses", number[1]]
        inc_avg_time = ["Average incoming impulse time", avg_time[0]]
        out_avg_time = ["Average outgoing impulse time", avg_time[1]]
        incoming_impulse_data = [line for line in impulses[0]] + [inc_number] + [inc_avg_time]
        incoming_impulse_data = [["Incoming impulses"]] + incoming_impulse_data
        outgoing_impulse_data = [line for line in impulses[1]] + [out_number] + [out_avg_time]
        outgoing_impulse_data = [["Outgoing impulses"]] + outgoing_impulse_data
        self._impulse_data = incoming_impulse_data + outgoing_impulse_data

    def _create_impulse_data_file(self, filename, total_impulse=False):
        if total_impulse:
            file = filename + "/total_impulses.csv"
        else:
            file = filename[:-4] + "_impulse.csv"
        data = [line for line in self._impulse_data]
        self._impulse_data = list()
        FileWriter.write_data_to_file(data=data, filename=file)

    def _parse_impulse_data_for_files(self):
        impulse_data = list()
        if len(self._files) > 0:
            for file in self._files:
                impulse_data += self._parse_impulses(file=file)
            self._impulse_data = [line.split(";") for line in impulse_data]
            file_name = self._files[0].rsplit(sep="/", maxsplit=1)[0]
            self._create_impulse_data_file(filename=file_name, total_impulse=True)
        else:
            print("No files in directory. Exiting program.")
            exit(1)

    def _parse_impulses(self, file):
        data = FileHandler.get_data_from_file(file)
        name = file.rsplit(sep="/", maxsplit=1)[1].split(sep="_")[1:3]
        name = name[0] + " " + name[1]
        impulse_data = [name]
        for line in data:
            if "Number of inc" in line or "Average inc" in line or "Number of outg" in line or "Average out" in line:
                impulse_data.append(line)
        return impulse_data
