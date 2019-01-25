import copy

from app.data_handler import DataHandler
from app.file_handler import FileHandler


class LogOrganizer:

    class LogOrganizerError(Exception):
        pass

    def __init__(self):
        self._raw_data = list()
        self._organized_data = list()
        self._node_name = str()
        self._time_interval_sec = int()
        self._current_entry_idx = int()
        self._last_entry_idx = int()
        self._number_of_columns = int()

    @property
    def organized_data(self):
        return self._organized_data

    @property
    def node_name(self):
        return self._node_name

    @property
    def time_interval_sec(self):
        return self._time_interval_sec

    def organize_log(self, filename, node_name, time_interval_sec):
        self._node_name = node_name
        self._time_interval_sec = time_interval_sec
        try:
            self._get_data(filename=filename)
        except FileNotFoundError:
            raise LogOrganizer.LogOrganizerError("file: {} does not exist".format(filename))
        self._organize_log()

    def _get_data(self, filename):
        self._raw_data = FileHandler.get_data_from_file(filename=filename)

    def _organize_log(self):
        self._get_number_of_columns()
        self._create_first_entry()
        while True:
            if self._create_next_entry():
                continue
            else:
                break
        print("Finished organizing log using time interval of {} seconds.".format(self._time_interval_sec))

    def _get_number_of_columns(self):
        first_entry = self._get_entry_at_idx(idx=0)
        first_entry = first_entry.split(";")
        self._number_of_columns = len(first_entry)

    def _get_entry_at_idx(self, idx):
        try:
            entry = self._raw_data[idx]
        except IndexError:
            raise LogOrganizer.LogOrganizerError("incorrect entry index: {} when retrieving entry data".format(idx))
        else:
            return entry

    def _create_first_entry(self):
        self._get_first_entry_idx()
        first_entry = copy.deepcopy(self._raw_data[self._current_entry_idx])
        self._organized_data.append(first_entry)

    def _get_first_entry_idx(self):
        for idx, entry in enumerate(self._raw_data):
            for value in entry.split(";"):
                if isinstance(DataHandler.convert_to_number(value=value), str):
                    break
            else:
                self._current_entry_idx = idx
                return

    def _create_next_entry(self):
        self._last_entry_idx = self._current_entry_idx
        try:
            next_entry_date = self._get_next_entry_date()
        except LogOrganizer.LogOrganizerError:
            return False
        if self._approximate_next_entry_date() < next_entry_date:
            self._create_duplicate_entry()
        elif self._approximate_next_entry_date() == next_entry_date:
            self._create_new_entry()
        else:
            self._create_averaged_entry()
        return True

    def _create_duplicate_entry(self):
        try:
            new_entry = copy.deepcopy(self._get_entry_at_idx(idx=self._current_entry_idx))
        except LogOrganizer.LogOrganizerError:
            raise LogOrganizer.LogOrganizerError("can't create duplicate data entry due to incorrect entry index: {}"
                                                 .format(self._current_entry_idx))
        new_entry = self._set_approximate_date_for_entry(entry=new_entry)
        self._organized_data.append(new_entry)

    def _set_approximate_date_for_entry(self, entry):
        new_entry_date = self._approximate_next_entry_date()
        new_entry_date = DataHandler.convert_to_string(value=new_entry_date)
        if isinstance(entry, str):
            entry = ";".join([new_entry_date] + entry.split(";")[1:])
        else:
            entry = ";".join([new_entry_date] + [DataHandler.convert_to_string(value=value) for value in entry[1:]])
        return entry

    def _create_new_entry(self):
        try:
            new_entry = copy.deepcopy(self._get_entry_at_idx(idx=self._current_entry_idx))
        except LogOrganizer.LogOrganizerError:
            raise LogOrganizer.LogOrganizerError("can't create new data entry due to incorrect entry index: {}"
                                                 .format(self._current_entry_idx))
        self._organized_data.append(new_entry)
        self._current_entry_idx += 1

    def _create_averaged_entry(self):
        new_entries = list()
        try:
            new_entries.append(self._get_entry_at_idx(idx=self._current_entry_idx))
        except LogOrganizer.LogOrganizerError:
            raise LogOrganizer.LogOrganizerError("can't create new averaged data entry due to incorrect entry index: "
                                                 "{}".format(self._current_entry_idx))
        for entry in self._raw_data[self._current_entry_idx + 1:]:
            if self._approximate_next_entry_date() > self._get_entry_date(entry):
                new_entries.append(entry)
                self._current_entry_idx += 1
            elif self._approximate_next_entry_date() == entry[0]:
                new_entries.append(entry)
                self._current_entry_idx += 1
                break
            else:
                last_entry = self._set_approximate_date_for_entry(entry=entry)
                new_entries.append(last_entry)
                self._current_entry_idx += 1
                break
        self._average_values_from_new_entries(entries=new_entries)

    def _average_values_from_new_entries(self, entries):
        new_entry = [0] * self._number_of_columns
        try:
            for entry in entries:
                for idx, column in enumerate(entry.split(";")):
                    new_entry[idx] += DataHandler.convert_to_float(column)
        except IndexError:
            raise LogOrganizer.LogOrganizerError("incorrect number of data columns at entry index: {}"
                                                 .format(self._current_entry_idx))
        number_of_new_entries = len(entries)
        new_entry = [DataHandler.convert_to_int(column / number_of_new_entries) for column in new_entry]
        new_entry = self._set_approximate_date_for_entry(entry=new_entry)
        self._organized_data.append(new_entry)

    def _get_next_entry_date(self):
        next_entry = self._get_entry_at_idx(idx=self._last_entry_idx + 1)
        date_of_next_entry = next_entry.split(";")[0]
        return DataHandler.convert_to_number(date_of_next_entry)

    def _approximate_next_entry_date(self):
        return self._get_last_entry_date() + self._time_interval_sec

    def _get_last_entry_date(self):
        last_organized_entry = self._organized_data[-1]
        date_of_last_organized_entry = last_organized_entry.split(";")[0]
        return DataHandler.convert_to_number(date_of_last_organized_entry)

    def _get_entry_date(self, entry):
        entry_date = entry.split(";")[0]
        return DataHandler.convert_to_number(entry_date)


class LogOrganizerDataExporter:

    @staticmethod
    def export_data(log_organizer):
        if not isinstance(log_organizer, LogOrganizer):
            raise LogOrganizer.LogOrganizerError("incorrect object type to export log data from")
        organized_data = log_organizer.organized_data
        filename = "data/" + log_organizer.node_name + "/log_organized_"
        time_interval = DataHandler.convert_to_string(log_organizer.time_interval_sec)
        filename += time_interval + ".csv"
        FileHandler.write_data_to_file(data=organized_data, filename=filename)
