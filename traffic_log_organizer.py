from app.log_organizer import LogOrganizer, LogOrganizerDataExporter
from app.log_splitter import LogSplitter, LogSplitterDateConverter


def traffic_log_organizer():
    while True:
        print("Welcome to Traffic Log Organizer.\n"
              "You can organize raw data by providing constant time interval\nand the program will create new .csv log "
              "file,\nwhere all data is separated by this time interval\n(averaging or duplicating entries when"
              "necessary).\n"
              "Files organized in this way can then be split into smaller files:\nby constant time interval (for"
              "example, daily or weekly logs),\nby specific dates (for example, from 01-01-2016 to 05-25-2016).\n")
        print("Do you want to organize (o) or split (s) log files? (o/s): ")
        while True:
            organize_or_split = input()
            if organize_or_split == "o":
                _organize_data()
                break
            elif organize_or_split == "s":
                _split_data()
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
    interval = 0
    try:
        print("Enter time interval (in seconds): ")
        interval = int(input())
    except TypeError:
        print("Time interval must be integer.")
    print('After finishing, file will be found in /data folder as "log_organized_{}.csv".'.format(interval))
    organizer = LogOrganizer()
    organizer.organize_log(data_file=file, time_interval_in_seconds=interval)
    LogOrganizerDataExporter.export_data(log_organizer=organizer)


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
          "604800 - 1 week\nEnter interval: ")
    interval = 0
    try:
        interval = int(input())
    except TypeError:
        print("Time interval must be integer.")
    splitter = LogSplitter(data_file=file, print_avg_and_max=print_averages, first_column_avg=2, last_column_avg=3,
                           first_column_max=4, last_column_max=5)
    splitter.split_log(time_interval_in_seconds=interval)
    print('After finishing, files will be found in /data/t_x folder as "log_x_y.csv",\nwhere x is time interval, y '
          'is file number.')


def _split_by_date(file, print_averages):
    print("Enter first date (format must be: DD-MM-YYYY): ")
    first_date = input()
    first_date = LogSplitterDateConverter.convert_date(date=first_date)
    print("Enter last date (format must be: DD-MM-YYYY): ")
    last_date = input()
    last_date = LogSplitterDateConverter.convert_date(date=last_date)
    splitter = LogSplitter(data_file=file, print_avg_and_max=print_averages, first_column_avg=2, last_column_avg=3,
                           first_column_max=4, last_column_max=5)
    splitter.split_log(start_date=first_date, end_date=last_date)
    print('After finishing, file will be found in data folder as "log_from_x_to_y.csv", where x and y are dates.')


if __name__ == "__main__":
    traffic_log_organizer()
