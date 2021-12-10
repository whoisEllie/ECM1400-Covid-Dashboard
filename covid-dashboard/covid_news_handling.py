"""
Handles news schedulers and API calls
"""
from datetime import timedelta, date
import logging
import sched
import time
import json
import os
import requests
from flask import Markup

scheduler = sched.scheduler(time.time, time.sleep)

scheduled_updates = []
news_list = []
current_news_titles = []
news_blacklist = []

directory_path = os.path.dirname(os.path.abspath(__file__)) 
new_path = os.path.join(directory_path, "config.json")
with open(new_path, "r", encoding="utf8") as jsonfile:
    config = json.load(jsonfile)
apiKey = config['apiKey']


def news_API_request(covid_terms: str = "Covid COVID-19 coronavirus") -> dict:
    """Request news database from the news API.

    Keyword arguments:
    covid_terms -- search terms using when fetching from the news API
    """
    terms = " OR ".join(covid_terms.split())
    if config['specify_sources'] is True:
        payload = {
            "apiKey": apiKey,
            "language": config['news_language'],
            "q": terms,
            "sortBy": config['news_api_sortBy'],
            "sources": config['sources']}
    else:
        payload = {
            "apiKey": apiKey,
            "language": config['news_language'],
            "q": terms,
            "sortBy": config['news_api_sortBy']}
    request = requests.get(config['news_api_url'], params=payload)
    logging.info("Successfully requested news data from the news API")
    return request.json()


def update_news(covid_terms: str = "Covid COVID-19 coronavirus"):
    """Update the news list.

    Called from widget_interface.py and update_data, updates all_news,
    and then sorts it to make sure blacklisted and already existing
    news elements don't get spawned. Sorts the news based on the
    date of publishing, with newest dates coming first in the list
    (on top of the widget stack)

    Keyword arguments:
    covid_terms -- string of terms, separated by a space which are
    used by the news_API to search for connected articles
    """
    global news_list
    try:
        all_news = news_API_request(covid_terms)['articles']
    except IndexError:
        logging.error("Failed to get NewsAPI with given terms %s",covid_terms)
        all_news = []
    length_cache = len(news_list)
    for element in all_news:
        if element['title'] in news_blacklist or (element['title'] in 
            current_news_titles):
            pass
        else:
            title = element['title']
            for word in config['blacklisted_strings']:
                if word in title:
                    title = title.replace(word, '')
            content = element['description'] + " (" + Markup(
                "<a target=""blank"" rel=""noopener noreferrer"" href=\"" +
                element['url'] + "\">" + "Read More" + "</a>") + ")"
            news_list.append(
                {"title": title, "content": content,
                "year": element['publishedAt']})
            current_news_titles.append(element['title'])
            logging.debug(
                "Successfuly added %s to the updates list",element['title'])
    news_list.sort(reverse=True, key=sort_by_date)
    if length_cache == len(news_list):
        logging.info(
            "Successfully processed the result from the news API, but\
                no new articles found")
    else:
        logging.info("Successfuly added new articles")


def sort_by_date(entry):
    """Return the entry of key 'year' for use in sorting"""
    return entry['year']


def schedule_news_updates(update_interval: str, update_name: str):
    """Schedule a news update using the sched module.

    Keyword arguments:
    update-interval -- the time at which the update should run,
    expected in the format %H:%M [parsed into usable data]
    update-name -- a unique identifier for the update,
    derived from the widget title
    """
    execute_time = calculate_interval(update_interval)
    try:
        scheduled_update = scheduler.enterabs(execute_time, 1, update_data,
            {update_interval: update_interval,
            update_name: update_name})
        scheduled_updates.append({"update": scheduled_update,
            "title": update_name, "time": update_interval})
        logging.info(
            "Sucessfully scheduled %s at %s",update_name,update_interval)
        logging.info("scheduler queue is: %s",scheduler.queue)
    except ValueError:
        logging.error(
        "ValueError thrown when scheduling update with\
             interval %s and name %s",execute_time,update_name)


def calculate_interval(update_interval: str = "00:00") -> str:
    """Calculate a timestamp for when to schedule covid updates.

    Generates a unixtime timestamp from an Hours:Minutes string,
    which is parsed into unix time that can then be used to schedule
    the update. If the given time has already passed, we set the
    update to happen the next time that time happes [i.e. tomorrow]

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
                time.strptime(
                    next_time,
                    '%Y-%m-%d %H:%M:%S'))
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
    update_news()
    widget_interface.update_site()
    for update in widget_interface.updates_list:
        if update_name == update['title']:
            if "daily" in update['content']:
                schedule_news_updates(update_interval, update_name)
                logging.info("Scheduled a new news update")
            else:
                widget_interface.remove_item(update, "news_item",
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
                    "Removed News update, scheduler queue is: %s",
                    scheduler.queue)
            except ValueError:
                logging.warning(
                    "Scheduler failed to cancel update %s,\
                        (this could be because it's already been cancelled!)",
                        scheduled_update)
                logging.warning("News scheduler queue is: %s",scheduler.queue)


def run_updates():
    """Run the scheduler, called from the widget_interface every 60s."""
    scheduler.run(blocking=False)
    logging.info("News data scheduler was run with blocking=False")