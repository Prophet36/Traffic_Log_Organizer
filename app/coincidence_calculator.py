import os

from app.data_handlers import DataHandler
from app.file_handlers import FileWriter, FileReader


class CoincidenceCalculator:

    def __init__(self):
        self._node_a_data = tuple()
        self._node_b_data = tuple()
        self._files = list()
        self._node_a_inc_start_date = 0
        self._node_a_out_start_date = 0
        self._node_b_inc_start_date = 0
        self._node_b_out_start_date = 0
        self._time_interval = 0
        self._node_a_name = None
        self._node_b_name = None
        self._coincidence_data = tuple()

    def calculate_coincidences(self, file_path_node_a, file_path_node_b, time_interval):
        self._time_interval = time_interval
        self._get_file_names_from_path(file_path=file_path_node_a)
        self._node_a_name = self._files[0].rsplit(sep="/", maxsplit=1)[0]
        self._node_a_data = self._get_impulse_data()
        self._get_file_names_from_path(file_path=file_path_node_b)
        self._node_b_name = self._files[0].rsplit(sep="/", maxsplit=1)[0]
        self._node_b_data = self._get_impulse_data()
        self._get_starting_points()
        self._calculate_coincidences()
        self._create_coincidence_file()

    def _get_file_names_from_path(self, file_path):
        self._files.clear()
        for file in os.listdir(file_path):
            if file.endswith("impulse.csv") and not file.endswith("impulses.csv"):
                self._files.append(file_path + "/" + str(file))

    def _get_impulse_data(self):
        inc_impulse_data = list()
        out_impulse_data = list()
        if len(self._files) > 0:
            for file in self._files:
                impulse_data = self._get_single_impulse_file_data(file=file)
                inc_impulse_data += impulse_data[0]
                out_impulse_data += impulse_data[1]
        else:
            print("No files in directory. Exiting program.")
            exit(1)
        return inc_impulse_data, out_impulse_data

    def _get_single_impulse_file_data(self, file):
        data = FileReader.get_file_data(file)
        incoming_data = True
        inc_impulse_data = list()
        out_impulse_data = list()
        for line in data:
            if "Incoming" in line:
                incoming_data = True
            elif "Outgoing" in line:
                incoming_data = False
            if "impulse" not in line:
                if incoming_data:
                    inc_impulse_data.append(line)
                else:
                    out_impulse_data.append(line)
        inc_impulse_data.sort(key=lambda x: x.split(";")[0])
        out_impulse_data.sort(key=lambda x: x.split(";")[0])
        return inc_impulse_data, out_impulse_data

    def _get_starting_points(self):
        self._node_a_inc_start_date = int(self._node_a_data[0][0].split(";")[0])
        self._node_a_out_start_date = int(self._node_a_data[1][0].split(";")[0])
        self._node_b_inc_start_date = int(self._node_b_data[0][0].split(";")[0])
        self._node_b_out_start_date = int(self._node_b_data[1][0].split(";")[0])

    def _calculate_coincidences(self):
        if self._node_a_inc_start_date >= self._node_b_inc_start_date:
            node_a = self._node_a_data[0]
            node_b = self._node_b_data[0]
        else:
            node_a = self._node_b_data[0]
            node_b = self._node_a_data[0]
        inc_coincidence_data = list()
        last_idx = 0
        for impulse_a in node_a:
            impulse_a_date = int(impulse_a.split(";")[0])
            for idx, impulse_b in enumerate(node_b[last_idx:], start=last_idx):
                impulse_b_date = int(impulse_b.split(";")[0])
                predicted_date = impulse_b_date + self._time_interval
                if impulse_b_date <= impulse_a_date <= predicted_date:
                    inc_coincidence_data.append(impulse_a)
                    last_idx = idx + 1
                    break
        if self._node_a_out_start_date >= self._node_b_out_start_date:
            node_a = self._node_a_data[1]
            node_b = self._node_b_data[1]
        else:
            node_a = self._node_b_data[1]
            node_b = self._node_a_data[1]
        out_coincidence_data = list()
        last_idx = 0
        for impulse_a in node_a:
            impulse_a_date = int(impulse_a.split(";")[0])
            for idx, impulse_b in enumerate(node_b[last_idx:], start=last_idx):
                impulse_b_date = int(impulse_b.split(";")[0])
                predicted_date = impulse_b_date + self._time_interval
                if impulse_b_date <= impulse_a_date <= predicted_date:
                    out_coincidence_data.append(impulse_a)
                    last_idx = idx + 1
                    break
        self._coincidence_data = inc_coincidence_data, out_coincidence_data

    def _create_coincidence_file(self):
        data = [["Incoming impulses coincidences"]]
        for item in self._coincidence_data[0]:
            data.append([item])
        data.append(["Outgoing impulses coincidences"])
        for item in self._coincidence_data[1]:
            data.append([item])
        file_name = self._node_b_name.rsplit("/")[-2]
        file_name = self._node_a_name + "/coincidence_with_node_" + file_name + ".csv"
        FileWriter.write_data_as_csv(data=data, filename=file_name)
