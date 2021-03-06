from app.log_organizer import LogOrganizer, LogOrganizerDataExporter
from app.log_splitter import LogSplitter, LogSplitterDateConverter
from app.impulse_calculator import ImpulseCalculator
from app.coincidence_calculator import CoincidenceCalculator


def traffic_log_organizer():
    while True:
        print("Welcome to Traffic Log Organizer.\n"
              "You can organize raw data by providing constant time interval\nand the program will create new .csv log "
              "file,\nwhere all data is separated by this time interval\n(averaging or duplicating entries when "
              "necessary).\n"
              "Files organized in this way can then be split into smaller files:\nby constant time interval (for "
              "example, daily or weekly logs),\nby specific dates (for example, from 01-01-2016 to 05-25-2016).\n"
              "Impulse data can be calculated from processed logs, and coincidences of impulses from other nodes.\n")
        print("Do you want to organize (o), split (s), calculate impulses (i), or coincidences? (o/s/i/c): ")
        while True:
            organize_or_split = input()
            if organize_or_split == "o":
                _organize_data()
                break
            elif organize_or_split == "s":
                _split_data()
                break
            elif organize_or_split == "i":
                _calculate_impulses()
                break
            elif organize_or_split == "c":
                _calculate_coincidences()
                break
            else:
                print("Incorrect option. Try again (o/s): ")
        print("Do you want to use Traffic Log Organizer again? (y/n): ")
        repeat = input()
        if repeat != "y":
            break
    print("Thank you for using Traffic Log Organizer!")


def _organize_data():
    print("Enter path and file name to organize: ")
    file = input()
    while True:
        try:
            print("Enter time interval in seconds:\n300 - 5 minutes\n1800 - 30 minutes\n7200 - 2 hours\n86400 - 1 day\n"
                  "604800 - 1 week\n2592000 - 1 month\n31536000 - 1 year\nEnter interval: ")
            interval = int(input())
        except ValueError:
            print("Time interval must be integer.")
        else:
            break
    print("Enter node name: ")
    node = input()
    node = node
    print('After finishing, file will be found in data/{} folder as "log_organized_{}.csv".'.format(node + "/",
                                                                                                    interval))
    organizer = LogOrganizer()
    try:
        organizer.organize_log(filename=file, time_interval_sec=interval, node_name=node)
        LogOrganizerDataExporter.export_data(log_organizer=organizer)
    except LogOrganizer.LogOrganizerError as e:
        print("An error occurred while organizing log: {}".format(e))


def _split_data():
    print("Enter path and file name to split: ")
    file = input()
    print("Do you want to split by constant time intervals (t) or by dates (d)? (t/d): ")
    while True:
        split_type = input()
        if split_type == "t" or split_type == "d":
            break
        else:
            print("Incorrect option. Try again (t/d): ")
    print("Do you want to print average and maximum values at the bottom of split log files? (y/n): ")
    while True:
        print_averages = input()
        if print_averages == "y" or print_averages == "n":
            break
        else:
            print("Incorrect option. Try again (y/n): ")
    if print_averages == "y":
        print_averages = True
    else:
        print_averages = False
    if split_type == "t":
        _split_by_time_interval(file=file, print_averages=print_averages)
    else:
        _split_by_date(file=file, print_averages=print_averages)


def _split_by_time_interval(file, print_averages):
    print("Enter time interval in seconds:\n300 - 5 minutes\n1800 - 30 minutes\n7200 - 2 hours\n86400 - 1 day\n"
          "604800 - 1 week\n2592000 - 1 month\n31536000 - 1 year\nEnter interval: ")
    interval = 0
    try:
        interval = int(input())
    except TypeError:
        print("Time interval must be integer.")
    print('After finishing, files will be found in /data/t_x folder as "log_x_y.csv",\nwhere x is time interval, y '
          'is file number.')
    splitter = LogSplitter(data_file=file, print_avg_and_max=print_averages, first_column_avg=2, last_column_avg=3,
                           first_column_max=4, last_column_max=5)
    splitter.split_log(time_interval_in_seconds=interval)


def _split_by_date(file, print_averages):
    print("Enter first date (format must be: D-M-YYYY): ")
    first_date = input()
    first_date = LogSplitterDateConverter.convert_date(date=first_date)
    print("Enter last date (format must be: D-M-YYYY): ")
    last_date = input()
    last_date = LogSplitterDateConverter.convert_date(date=last_date)
    print('After finishing, file will be found in data folder as "log_from_x_to_y.csv", where x and y are dates.')
    splitter = LogSplitter(data_file=file, print_avg_and_max=print_averages, first_column_avg=2, last_column_avg=3,
                           first_column_max=4, last_column_max=5)
    splitter.split_log(start_date=first_date, end_date=last_date)


def _calculate_impulses():
    print("Enter path with logs to calculate impulses for: ")
    path = input()
    print('After finishing, files will be found in {} folder, ending with "impulse.csv".'.format(path))
    calculator = ImpulseCalculator()
    calculator.calculate_impulses_in_directory(file_path=path)
    calculator.parse_impulse_data_in_directory(file_path=path)


def _calculate_coincidences():
    print("Enter path with impulse logs of first node to calculate coincidences for: ")
    node_a = input()
    print("Enter path with impulse logs of second node to calculate coincidences with: ")
    node_b = input()
    print("Enter time interval (in seconds) of logs impulse logs were based on:\n300 - 5 minutes\n1800 - 30 minutes\n"
          "7200 - 2 hours\n86400 - 1 day\n604800 - 1 week\n2592000 - 1 month\n31536000 - 1 year\nEnter interval: ")
    interval = int(input())
    print('After finishing, files will be found in {} folder, with name starting as "coincidence_with_node".'
          .format(node_a))
    coincidence_calculator = CoincidenceCalculator()
    coincidence_calculator.calculate_coincidences(file_path_node_a=node_a, file_path_node_b=node_b,
                                                  time_interval=interval)


if __name__ == "__main__":
    traffic_log_organizer()
