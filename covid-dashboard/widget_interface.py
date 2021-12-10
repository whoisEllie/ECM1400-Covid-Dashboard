"""
Handles interactions between the flask frontend and the python backend
"""
import logging
import sched
import time
import json
import os
from flask import current_app as app
from flask.templating import render_template
from flask import request
import covid_news_handling
import covid_data_handler

updates_list = []
cumulative_deaths = "n/A"
hospital_cases = "n/A"
national_7day_infections = "n/A"
local_7day_infections = "n/A"

scheduler = sched.scheduler(time.time, time.sleep)

directory_path = os.path.dirname(os.path.abspath(__file__)) 
new_path = os.path.join(directory_path, "config.json")
with open(new_path, "r", encoding="utf8") as jsonfile:
    config = json.load(jsonfile)


def remove_item(update: str, element_name: str,
                remove_list: list, update_finished: bool = False):
    """Remove an item from a widget column.

    Removes an element from a column, be that a news article or
    update widget. In the case of a news article, it updates the
    blacklist to make sure that we don't see that same article again.
    In the case of an update item, it cancels the scheduled update
    within covid_data_handler.py

    Keyword arguments:
    update -- dictionary which holds information about the item (title)
    element name -- string which denotes whether to look for news or
    updates
    remove_list -- the list from which to remove the item
    update_finished -- whether the event is being closed [in the case
    that it has finished running] (False by default)
    """
    if request.args.get(
            element_name) == update["title"] or update_finished is True:
        if len(remove_list) > 0:
            if element_name == "update_news":
                covid_news_handling.news_blacklist.append(update['title'])
            if element_name == "update_item" and update_finished is False:
                covid_data_handler.remove_update(update['title'])
            try:
                remove_list.remove(update)
            except IndexError:
                logging.error(
                    "Failed to remove item %s from list",update['title'])


def generate_name(comparison_list: list, prefix: str) -> str:
    """Generates cascading event names for updates

    Makes sure that 2 updates are never called the same thing by
    appending a number to the end of them, as well as applying a
    prefix in order to be able to easily differentiate between Covid
    and News updates

    Keyword arguments:
    comparison_list -- the list against which to compare names
    prefix -- the prefix to assign to names (Covid/News) to
    differentiate them
    """
    update_name = ""
    counter = 0
    for element in comparison_list:
        name = element['title']
        if counter > 0:
            offset = (len(name) - len(prefix + request.args.get('two')))
            name = name[:-offset]
        if name == prefix + request.args.get('two'):
            counter += 1
    if counter == 0:
        update_name = prefix + request.args.get('two')
    else:
        update_name = prefix + request.args.get('two') + '-' + str(counter)
    return update_name


def set_updates():
    """Update scheduler, called from update_site.

    Passes selected time to covid_data_handler and news_data_handling
    in order to schedule the relevant updates, as well as updating
    widgets on the main page. Parses data coming from the form
    """
    update_time = request.args.get('alarm')
    update_time.replace("%3A", ":", 1)
    if request.args.get('covid-data') == 'covid-data':
        update_content = ""
        if request.args.get('repeat'):
            update_content = f"Covid data will be updated daily \
                at: {update_time}"
        else:
            update_content = f"Covid data will be updated at: {update_time}"
        update_name = generate_name(updates_list, 'Covid data ')
        covid_data_handler.schedule_covid_updates(update_time, update_name)
        updates_list.append({"title": update_name, "content": update_content})
    if request.args.get('news') == 'news':
        covid_news_handling.update_news()
        update_content = ""
        if request.args.get('repeat'):
            update_content = f"News data will be updated daily \
                at: {update_time}"
        else:
            update_content = f"News data will be updated at: {update_time}"
        update_name = generate_name(updates_list, 'News data ')
        covid_news_handling.schedule_news_updates(update_time, update_name)
        updates_list.append({"title": update_name, "content": update_content})


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def update_site():
    """Called on reload, updates site and receives input.

    Receives input from the website on all updates, reacts to a GET
    method to perform various gunctions around updating data/schedule
    data, such as updating news and removing updates, while returning
    the index.html file as a render_template with all the appropriate
    variables passed through
    """
    covid_data_handler.run_updates()
    covid_news_handling.run_updates()
    if request.method == "GET":
        for update in updates_list:
            remove_item(update, 'update_item', updates_list)
        for article in covid_news_handling.news_list:
            remove_item(article, 'update_news', covid_news_handling.news_list)
        if request.args.get('two'):
            set_updates()

    final_news = covid_news_handling.news_list[:config['max_articles']]

    return render_template("index.html",
        updates=updates_list,
        news_articles=final_news,
        location=config['national_location'],
        nation_location=config['local_location'],
        local_7day_infections=local_7day_infections,
        national_7day_infections=national_7day_infections,
        hospital_cases=(f"National hospital cases: {hospital_cases}"),
        deaths_total=(f"National cumulative deaths: {cumulative_deaths}"),
        title=config['title'],
        image=config['image_path'])
