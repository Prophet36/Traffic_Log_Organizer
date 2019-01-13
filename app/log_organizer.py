import copy

from app.file_handler import FileReader, FileWriter


class LogOrganizer:

    def __init__(self):
        self._data = list()
        self._organized_data = list()
        self._date_of_first_data_entry = 0
        self._time_interval = 300
        self._current_data_position = 2
        self._last_data_position = 2

    def organize_log(self, filename, time_interval=300, first_entry=2):
        self._time_interval = time_interval
        self._current_data_position = first_entry
        if self._get_data(filename):
            self._time_interval = time_interval
            self._organize_log()

    def _get_data(self, filename):
        try:
            self._data = FileReader.get_file_data(filename)
        except FileNotFoundError:
            return False
        else:
            return True

    def _organize_log(self):
        self._split_data()
        self._create_first_data_entry()
        while True:
            if self._find_next_time_interval():
                continue
            else:
                break
        self._write_to_file()

    def _split_data(self):
        data = list()
        for line in self._data:
            data.append(line.split(";"))
        self._data = data

    def _create_first_data_entry(self):
        self._organized_data.append(self._data[self._last_data_position])
        self._date_of_first_data_entry = int(self._organized_data[0][0])

    def _find_next_time_interval(self):
        self._last_data_position = self._current_data_position
        if self._last_data_position + 1 >= len(self._data):
            return False
        if self._approximate_next_date() < self._get_next_date():
            self._create_duplicate_data_entry()
        elif self._approximate_next_date() == self._get_next_date():
            self._create_new_data_entry()
        else:
            self._create_new_averaged_data_entry()
        return True

    def _create_duplicate_data_entry(self):
        new_entry = copy.deepcopy(self._data[self._current_data_position])
        new_entry[0] = str(int(self._organized_data[-1][0]) + int(self._time_interval))
        self._organized_data.append(new_entry)

    def _create_new_data_entry(self):
        new_entry = copy.deepcopy(self._data[self._current_data_position + 1])
        self._organized_data.append(new_entry)
        self._current_data_position += 1

    def _create_new_averaged_data_entry(self):
        new_entries = list()
        new_entries.append(self._data[self._current_data_position + 1])
        for entry in self._data[self._current_data_position + 1:]:
            if self._current_data_position + 1 >= len(self._data):
                break
            if self._approximate_next_date() > int(entry[0]):
                new_entries.append(entry)
                self._current_data_position += 1
            elif self._approximate_next_date() == entry[0]:
                new_entries.append(entry)
                self._current_data_position += 1
                break
            else:
                new_entries.append(entry)
                new_entries[-1][0] = self._approximate_next_date()
                self._current_data_position += 1
                break
        self._average_new_entries(new_entries)

    def _average_new_entries(self, new_entries):
        sum_of_avg_incoming = 0
        sum_of_avg_outgoing = 0
        sum_of_max_incoming = 0
        sum_of_max_outgoing = 0
        for entry in new_entries:
            sum_of_avg_incoming += int(entry[1])
            sum_of_avg_outgoing += int(entry[2])
            sum_of_max_incoming += int(entry[3])
            sum_of_max_outgoing += int(entry[4])
        number_of_new_entries = len(new_entries)
        avg_incoming = str(sum_of_avg_incoming / number_of_new_entries)
        avg_outgoing = str(sum_of_avg_outgoing / number_of_new_entries)
        max_incoming = str(sum_of_max_incoming / number_of_new_entries)
        max_outgoing = str(sum_of_max_outgoing / number_of_new_entries)
        new_entry = [str(self._approximate_next_date()), avg_incoming, avg_outgoing, max_incoming, max_outgoing]
        self._organized_data.append(new_entry)

    def _get_current_date(self):
        return int(self._organized_data[-1][0])

    def _get_next_date(self):
        return int(self._data[self._last_data_position + 1][0])

    def _approximate_next_date(self):
        return int(self._get_current_date() + self._time_interval)

    def _write_to_file(self):
        filename = "../data/log_organized_"
        interval_as_str = str(self._time_interval)
        filename += interval_as_str
        filename += ".csv"
        FileWriter.write_data_as_csv(data=self._organized_data, filename=filename)


if __name__ == "__main__":
    organizer = LogOrganizer()
    print("Enter path and file name to organize: ")
    file = input()
    print("Enter time interval (in seconds): ")
    interval = int(input())
    print('After finishing, file will be found in data folder as "log_organized_x.csv",\nwhere x is time interval.')
    organizer.organize_log(filename=file, time_interval=interval)
