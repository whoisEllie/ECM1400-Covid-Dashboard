"""
Handles covid schedulers and API calls
"""
import csv
from datetime import timedelta, date
import sched
import time
import logging
import json
import os
from typing import Union
from uk_covid19 import Cov19API

scheduler = sched.scheduler(time.time, time.sleep)

scheduled_updates = []

directory_path = os.path.dirname(os.path.abspath(__file__)) 
new_path = os.path.join(directory_path, "config.json")
with open(new_path, "r", encoding="utf8") as jsonfile:
    config = json.load(jsonfile)


def parse_csv_data(input_csv: str) -> list:
    """Parse a csv into a 2d list.

    Parses a csv file into a 2d list, separating rows with a ,

    csv_filename -- system path to a csv file containing data to
    be parsed
    """
    csvlist = []
    with open(input_csv, newline='', encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            csvlist.append(row)
        logging.info("Parsed CSV data")
        return csvlist


def is_integer(value: any) -> bool:
    """Check a value to see if it is an integer.

    Checks to see if a value is
    an integer, returning True if it is. Used to find the most
    recent valid value in find_recent_value.
    Keyword arguments:
    value -- any value, checked to see if it is an integer
    """
    try:
        value = int(value)
    except ValueError:
        return False
    except TypeError:
        return False
    else:
        logging.info("is_integer returned %s", value)
        return True


def find_recent_value(test_dictionary: list, indexname: str) -> int:
    """Find the most recent value for a category in a csv dictionary.

    Finds the most recent value in a csv datasheet by iterating through
    until the selected value returns true to an is_integer check.
    Used to make sure the value we are taking is the most recent one
    that is valid.

    Keyword arguments:
    data -- the 2d list to iterate through
    valuename -- the name of the vale which to iterate through
    """
    temp = 0
    index = test_dictionary[0].index(indexname)
    counter = 1
    try:
        temp = (test_dictionary[counter])[index]
    except IndexError:
        logging.error("IndexError in find_recent_value for value %s",temp)
        return None
    while not is_integer(temp):
        counter += 1
        try:
            temp = (test_dictionary[counter])[index]
        except IndexError:
            logging.error("IndexError in find_recent_value for value %s",temp)
            return None
    logging.info("Most recent value for %s is %s",indexname, temp)
    return int(temp)


def sum_recent_values(data: list, indexname: str, number: int = 7) -> int:
    """Return the sum of a set number of the most recent values.

    Sums the most recent values of a category in order to obtain an
    'X-day' summation. Only counts up with integer values thanks to
    the is_integer test

    Keyword arguments:
    data -- the 2d list to iterate through
    indexname -- the name of the index which to iterate through 
    number -- the amount of iterations to calculate
    (set to 7 [one week] by default)
    """
    index = data[0].index(indexname)
    templist = []
    counter = 0
    finalval = 0
    while len(templist) != number:
        if counter - 1 >= 0:
            tempcounter = counter - 1
        else:
            tempcounter = counter
        try:
            int_test = (data[tempcounter])[index]
        except IndexError:
            logging.error(
                "IndexError in find_recent_value for value %s",
                (data[counter])[index])
        if is_integer(int_test):
            try:
                templist.append((data[counter])[index])
            except IndexError:
                logging.error(
                    "IndexError in find_recent_value for value %s",
                    (data[counter])[index])
        counter += 1
    for i in range(len(templist)):
        finalval += int(templist[i])
    logging.info("Sum of most recent values for %s is %s",indexname, finalval)
    return finalval


def process_covid_csv_data(data_to_process: Union[list, dict]) -> int:
    """Process covid data into values used by index.html.

    Processes csv data into values usable by
    index.html, exctracting cumulative 7 day values for infections,
    hospital case data, and cumulative death data through the use of
    above-defined functions such as sum_recent_values

    Keyword arguments:
    data_to_process -- a 2d list or dictionary containing the data
    about national covid cases. In the case of a dictionary, it is
    converted into a csv file as this function's existence is
    necessitated through a test function
    """
    try:
        data_to_process[0]
    except KeyError:
        data_to_process = dict_to_csv(data_to_process)

    cumulative_deaths = find_recent_value(data_to_process,
        "cumDailyNsoDeathsByDeathDate")

    national_7day_infections = sum_recent_values(data_to_process,
        "newCasesBySpecimenDate", 7)

    hospital_cases = find_recent_value(data_to_process,
        "hospitalCases")

    logging.info(
        "Processed cumulative deaths as %s, 7 day infections\
            as %s, and hospital cases as %s",cumulative_deaths,
            national_7day_infections,
            hospital_cases)
    return national_7day_infections, hospital_cases, cumulative_deaths


def dict_to_csv(input_dictionary):
    """Convert a dictionary into a csv-type 2d list

    A function that converts the key values of a dictionary into rows
    of a csv file, in order to function properly with the already
    existing process_csv_data, which remains in order for
    test_covid_csv_data to pass. This is necessary as covid_API_request
    must return a dictionary according to test_covid_API_request

    Keyword arguments:
    input_dictionary -- the dictionary to be converted into a csv
    """
    return_csv = []
    return_csv.append(["areaCode", "areaName", "areaType",
        "cumDailyNsoDeathsByDeathDate", "hospitalCases",
        "newCasesBySpecimenDate"])
    for key in input_dictionary:
        loop_dict = input_dictionary[key]
        return_csv.append([loop_dict["areaCode"], loop_dict["areaName"],
            loop_dict["areaType"], loop_dict["cumDailyNsoDeathsByDeathDate"],
            loop_dict["hospitalCases"], loop_dict["newCasesBySpecimenDate"]])
    logging.info("Successfully parsed dictionary to csv")
    return return_csv


def covid_API_request(location: str = "England",
                      location_type: str = "nation"):
    """Request data from the British Government's covid API.

    Sends a covid-API request, returns this
    data as a csv file, which keeps track of this data, and allow it to
    then be unpacked by parse_csv_data

    Keyword arguments:
    national_location -- the location to use for national covid data
    requests (set to England by default)
    national_location_type -- the location type that corresponds with
    national_location, as defined by the covid-API
    (set to nation by default)
    """
    england_only = [
        f'areaType={location_type}',
        f'areaName={location}'
    ]
    cases_and_deaths = {
        "areaCode": "areaCode",
        "areaName": "areaName",
        "areaType": "areaType",
        "date": "date",
        "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
        "hospitalCases": "hospitalCases",
        "newCasesBySpecimenDate": "newCasesBySpecimenDate"
    }

    covid_data = Cov19API(filters=england_only,
                            structure=cases_and_deaths).get_json()['data']
    logging.info("Successfully called Covid API for %s",location)
    return reformat_data(covid_data)

def reformat_data(input_dict):
    """Reformat dictionary into a more usable style.

    Reformats an input dictionary into a more usable, iterable
    style, as is expected by future functions and for readability

    Keyword arguments:
    input_dict -- the dictionary to reformat
    """
    dateslist = []
    for entry in input_dict:
        dateslist.append(entry['date'])
    counter = 0
    data_dictionary = {}
    for entry in dateslist:
        data_dictionary[entry] = {'areaCode': input_dict[counter]['areaCode'],
        'areaName': input_dict[counter]['areaName'],
        'areaType': input_dict[counter]['areaType'],
        'cumDailyNsoDeathsByDeathDate': input_dict[counter]['cumDailyNsoDeathsByDeathDate'],
        'hospitalCases': input_dict[counter]['hospitalCases'],
        'newCasesBySpecimenDate': input_dict[counter]['newCasesBySpecimenDate']
        }
        counter += 1

    logging.info("Successfuly reformatted dictionary")
    return data_dictionary


def schedule_covid_updates(update_interval: str, update_name: str):
    """Schedule a covid update using the sched module.

    Keyword arguments:
    update-interval -- the time at which the update should run,
    expected in the format %H:%M [parsed into usable data]
    update-name -- a unique identifier for the update, derived from the widget title
    """
    execute_time = calculate_interval(update_interval)
    try:
        scheduled_update = scheduler.enterabs(execute_time, 1, update_data,
                                              {update_interval: update_interval,
                                              update_name: update_name})
        scheduled_updates.append({"update": scheduled_update, "title": update_name,
                                  "time": update_interval})
        logging.info(
            "Sucessfully scheduled %s at %s",update_name, update_interval)
        logging.info("scheduler queue is: %s",scheduler.queue)
    except ValueError:
        logging.error(
            "ValueError thrown when scheduling update with interval %s and\
            name %s",execute_time, update_name)


def calculate_interval(update_interval: str = "00:00") -> str:
    """Calculate a timestamp for when to schedule covid updates.

    Generates a unixtime timestamp from an Hours:Minutes string,
    which is parsed into unix time that can then be used to schedule
    the update. If the given time has already passed, we set the update
    to happen the next time that time happes [i.e. tomorrow]

    update-interval -- the time at which the update should run,
    expected in the format %H:%M [parsed into usable data]
    """
    update_interval = str(update_interval).split(":")
    update_hour = update_interval[0]
    try:
        update_minute = update_interval[1]
    except IndexError:
        update_minute = "00"
    next_time = str(date.today()) + ' ' + update_hour + \
        ":" + update_minute + ':00'
    execute_time = time.strptime(next_time, '%Y-%m-%d %H:%M:%S')
    execute_time = time.mktime(execute_time)
    try:
        if time.time() > execute_time:
            next_time = (str((date.today() + timedelta(days=1))) +
                         ' ' + update_hour + ":" + update_minute + ':00')
            execute_time = time.mktime(
                time.strptime(next_time, '%Y-%m-%d %H:%M:%S'))
    except TypeError:
        logging.error("TypeError when parsing time")
    logging.info(
        "Successfuly parsed %s, next call is at: %s",update_interval,
        next_time)
    return execute_time


def update_data(update_interval: str, update_name: str):
    """Update data after an update has run.

    Allows for rescheduling updates and calling an API request on
    completion of a scheduled update. Checks to see if the update_name
    contains the word "daily" [assigned for repeating updates] and if
    so repeats it, if not removes the widget

    Keyword arguments:
    update-interval -- the time at which the update should run,
    expected in the format %H:%M
    update-name -- a unique identifier for the update, typically
    derived from the widget title
    """
    import widget_interface
    widget_interface.local_7day_infections = process_covid_csv_data(
        covid_API_request(config['local_location'],
        config['local_location_type']))[0]
    (widget_interface.national_7day_infections, 
        widget_interface.hospital_cases,
        widget_interface.cumulative_deaths) = process_covid_csv_data(
        covid_API_request(config['national_location'],
        config['national_location_type']))
    for update in widget_interface.updates_list:
        if update_name == update['title']:
            if "daily" in update['content']:
                try:
                    schedule_covid_updates(update_interval, update_name)
                    logging.info("Scheduled a new covid update")
                except ValueError:
                    logging.error(
                        "Failed to schedule covid update %s",update_name)
            else:
                widget_interface.remove_item(update, "update_item",
                    widget_interface.updates_list, True)
                logging.info("Removed widget %s",update['title'])


def remove_update(title: str):
    """Remove an update from the scheduler queue.

    Keyword arguments:
    title -- the name of the update which to remove,
    corresponding to update_name
    """
    for update in scheduled_updates:
        if update['title'] == title:
            scheduled_update = update['update']
            try:
                scheduler.cancel(scheduled_update)
                logging.info(
                    "Removed Covid update, scheduler queue is: %s",
                    scheduler.queue)
            except ValueError:
                logging.warning(
                    "Scheduler failed to cancel update %s, (this could be\
                    because it's already been cancelled!)",scheduled_update)
                logging.warning("Covid scheduler queue is: %s",
                    scheduler.queue)


def run_updates():
    """Run the scheduler, called from the widget_interface every 60s."""
    scheduler.run(blocking=False)
    logging.info("Covid data scheduler was run with blocking=False")