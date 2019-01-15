import copy

from app.file_handlers import FileReader, FileWriter
from app.data_handlers import DataHandler


class LogOrganizer:

    def __init__(self):
        self._data = list()
        self._organized_data = list()
        self._time_interval_in_seconds = 0
        self._current_data_index = 0
        self._last_data_index = 0
        self._number_of_data_columns = 0

    @property
    def time_interval_in_seconds(self):
        return self._time_interval_in_seconds

    @property
    def organized_data(self):
        return self._organized_data

    def organize_log(self, data_file, time_interval_in_seconds=300, index_of_first_entry=1):
        self._time_interval_in_seconds = time_interval_in_seconds
        self._current_data_index = index_of_first_entry
        try:
            self._get_data(data_file=data_file)
        except FileNotFoundError:
            print("File {} does not exist. Exiting program.".format(data_file))
            exit(1)
        else:
            self._time_interval_in_seconds = time_interval_in_seconds
            self._organize_log()

    def _get_data(self, data_file):
        self._data = FileReader.get_file_data(data_file)

    def _organize_log(self):
        self._split_and_convert_data_entries()
        self._set_number_of_data_columns()
        self._create_first_data_entry()
        while True:
            if self._find_next_time_interval():
                continue
            else:
                break
        print("Finished organizing log using time interval of {} seconds.".format(self._time_interval_in_seconds))

    def _split_and_convert_data_entries(self):
        self._data = [line.split(";") for line in self._data]
        self._convert_data_to_int()

    def _convert_data_to_int(self):
        self._data = [[DataHandler.convert_to_int(value=item) for item in line] for line in self._data]

    def _set_number_of_data_columns(self):
        self._number_of_data_columns = len(self._data[0])

    def _create_first_data_entry(self):
        first_entry = copy.deepcopy(self._data[self._current_data_index])
        self._organized_data.append(first_entry)

    def _find_next_time_interval(self):
        self._last_data_index = self._current_data_index
        if self._last_data_index + 1 >= len(self._data):
            return False
        if self._approximate_next_date() < self._get_next_date():
            self._create_duplicate_data_entry()
        elif self._approximate_next_date() == self._get_next_date():
            self._create_new_data_entry()
            self._current_data_index += 1
        else:
            self._create_new_averaged_data_entry()
        return True

    def _create_duplicate_data_entry(self):
        new_entry = copy.deepcopy(self._data[self._current_data_index])
        new_entry = self._set_correct_date_for_duplicate_data_entry(data_entry=new_entry)
        self._organized_data.append(new_entry)

    def _set_correct_date_for_duplicate_data_entry(self, data_entry):
        date_of_previous_data_entry = self._organized_data[-1][0]
        data_entry[0] = date_of_previous_data_entry + self._time_interval_in_seconds
        return data_entry

    def _create_new_data_entry(self):
        new_entry = copy.deepcopy(self._data[self._current_data_index + 1])
        self._organized_data.append(new_entry)

    def _create_new_averaged_data_entry(self):
        new_entries = list()
        new_entries.append(self._data[self._current_data_index + 1])
        for entry in self._data[self._current_data_index + 1:]:
            if self._current_data_index + 1 >= len(self._data):
                break
            if self._approximate_next_date() > int(entry[0]):
                new_entries.append(entry)
                self._current_data_index += 1
            elif self._approximate_next_date() == entry[0]:
                new_entries.append(entry)
                self._current_data_index += 1
                break
            else:
                new_entries.append(entry)
                new_entries[-1][0] = self._approximate_next_date()
                self._current_data_index += 1
                break
        self._average_values_from_new_data_entries(data_entries=new_entries)

    def _average_values_from_new_data_entries(self, data_entries):
        data_columns = [0] * self._number_of_data_columns
        try:
            for entry in data_entries:
                for idx, column in enumerate(data_columns):
                    data_columns[idx] += entry[idx]
        except IndexError:
            print("Incorrect number of data columns at line {}. Exiting program.".format(self._current_data_index))
            exit(1)
        else:
            number_of_new_entries = len(data_entries)
            data_columns = [column/number_of_new_entries for column in data_columns]
            data_columns[0] = self._approximate_next_date()
            new_entry = data_columns
            self._organized_data.append(new_entry)

    def _get_current_date(self):
        return self._organized_data[-1][0]

    def _get_next_date(self):
        return int(self._data[self._last_data_index + 1][0])

    def _approximate_next_date(self):
        return self._get_current_date() + self._time_interval_in_seconds


class LogOrganizerDataExporter:

    @staticmethod
    def export_data(log_organizer):
        if not isinstance(log_organizer, LogOrganizer):
            print("Can't extract organized data. Exiting program.")
            return
        data = log_organizer.organized_data
        filename = "../data/log_organized_"
        interval_as_str = str(log_organizer.time_interval_in_seconds)
        filename += interval_as_str
        filename += ".csv"
        FileWriter.write_data_as_csv(data=data, filename=filename)


if __name__ == "__main__":
    print("Enter path and file name to organize: ")
    file = input()
    print("Enter time interval (in seconds): ")
    interval = int(input())
    print('After finishing, file will be found in data folder as "log_organized_{}.csv".'.format(interval))
    organizer = LogOrganizer()
    organizer.organize_log(data_file=file, time_interval_in_seconds=interval)
    LogOrganizerDataExporter.export_data(log_organizer=organizer)
