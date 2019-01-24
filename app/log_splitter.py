import calendar
import datetime

from app.data_handlers import DataHandler
from app.file_handlers import FileReader, FileWriter


class LogSplitter:

    def __init__(self, data_file, print_avg_and_max=False, first_column_avg=None, last_column_avg=None,
                 first_column_max=None, last_column_max=None):
        self._print_avg_and_max = print_avg_and_max
        self._first_column_avg = first_column_avg
        self._last_column_avg = last_column_avg
        self._first_column_max = first_column_max
        self._last_column_max = last_column_max
        try:
            data = FileReader.get_file_data(filename=data_file)
        except FileNotFoundError:
            print("File {} does not exist. Exiting program.".format(data_file))
        else:
            self._file_path = data_file.rsplit(sep="/", maxsplit=1)[0]
            data = [line.split(";") for line in data]
            data = [[DataHandler.convert_to_float(value=item) for item in line] for line in data]
            data = [[DataHandler.convert_to_int(value=item) for item in line] for line in data]
            self._data = data

    def split_log(self, time_interval_in_seconds=None, start_date=None, end_date=None):
        if time_interval_in_seconds is not None:
            self._split_log_by_intervals(time_interval_in_seconds=time_interval_in_seconds)
        elif start_date is not None or end_date is not None:
            self._split_log_by_date(start_date=start_date, end_date=end_date)
        else:
            print("Insufficient parameter data. Exiting program.")
            exit(1)

    def _split_log_by_intervals(self, time_interval_in_seconds):
        current_time = self._data[0][0]
        file_number = 0
        current_index = 0
        while True:
            file_number += 1
            current_time += time_interval_in_seconds
            split_data = list()
            filename = self._get_file_name(time_interval_in_seconds, file_number)
            for idx, line in enumerate(self._data[current_index:], start=current_index):
                if line[0] >= current_time:
                    current_index = idx
                    self._create_split_log(data=split_data, filename=filename)
                    break
                split_data.append(line)
            else:
                return

    def _get_file_name(self, time_interval_in_seconds, file_number):
        if time_interval_in_seconds == 300:
            time_in = "5min"
        elif time_interval_in_seconds == 1800:
            time_in = "30min"
        elif time_interval_in_seconds == 7200:
            time_in = "2h"
        elif time_interval_in_seconds == 86400:
            time_in = "day"
        elif time_interval_in_seconds == 604800:
            time_in = "week"
        elif time_interval_in_seconds == 31536000:
            time_in = "year"
        else:
            time_in = str(time_interval_in_seconds) + "sec"
        file_name = self._file_path + "/t_" + str(time_in) + "/log_" + str(time_in) + "_" + str(file_number) + ".csv"
        return file_name

    def _create_split_log(self, data, filename):
        if self._print_avg_and_max:
            data = LogSplitterDataCalculator.calculate_total_average(data=data, first_column=self._first_column_avg,
                                                                     last_column=self._last_column_avg)
            data = LogSplitterDataCalculator.calculate_max_value(data=data, first_column=self._first_column_max,
                                                                 last_column=self._last_column_max)
        FileWriter.write_data_as_csv(data=data, filename=filename)

    def _split_log_by_date(self, start_date, end_date):
        file_name = self._file_path + "/log"
        if start_date is not None:
            file_name += "_from_" + str(start_date)
        if end_date is not None:
            file_name += "_to_" + str(end_date)
        file_name += ".csv"
        split_file = list()
        for idx, line in enumerate(self._data):
            if start_date is not None:
                if int(line[0]) < int(start_date):
                    continue
            if end_date is not None:
                if int(line[0]) >= int(end_date):
                    break
                split_file.append(line)
            else:
                split_file.append(line)
        self._create_split_log(data=split_file, filename=file_name)


class LogSplitterDataCalculator:

    @staticmethod
    def calculate_total_average(data, first_column, last_column):
        total_bits = [0] * (last_column - first_column + 1)
        total_time = 0
        for idx, line in enumerate(data):
            try:
                time_difference = line[0] - data[idx - 1][0]
                if time_difference < 0:
                    time_difference = 0
                total_time += time_difference
                for cidx, column in enumerate(line[first_column - 1:last_column]):
                    total_bits[cidx] += line[cidx + first_column - 1] * time_difference
            except TypeError:
                continue
        average_bits = [column / total_time for column in total_bits]
        last_entry = ["Average (bit/s)"] + average_bits
        data_with_averages = [line for line in data + [last_entry]]
        average_bits_in_kilobytes = [column / 1024 * 8 for column in average_bits]
        last_entry = ["Average (kB/s)"] + average_bits_in_kilobytes
        data_with_averages = [line for line in data_with_averages + [last_entry]]
        return data_with_averages

    @staticmethod
    def calculate_max_value(data, first_column, last_column):
        max_values = [0] * (last_column - first_column + 1)
        for line in data:
            try:
                for idx, column in enumerate(line[first_column - 1:last_column]):
                    if line[idx + first_column - 1] > max_values[idx]:
                        max_values[idx] = line[idx + first_column - 1]
            except TypeError:
                continue
        last_entry = ["Maximum (bit/s)"] + max_values
        data_with_maximums = [line for line in data + [last_entry]]
        max_values_in_kilobytes = [value / 1024 * 8 for value in max_values]
        last_entry = ["Maximum (kB/s)"] + max_values_in_kilobytes
        data_with_maximums = [line for line in data_with_maximums + [last_entry]]
        return data_with_maximums


class LogSplitterDateConverter:

    @staticmethod
    def convert_date(date):
        time = date.split("-")
        day = int(time[0])
        month = int(time[1])
        year = int(time[2])
        dt = datetime.datetime(year, month, day)
        ut = calendar.timegm(dt.timetuple())
        return ut
