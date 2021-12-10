# Welcome to ECM1400-Covid-Dashboard!

### What is ECM1400-Covid-Dashboard?

ECM1400-Covid-Dashboard is, as the name suggests, a dashboard - built with Jinja and Flask, utilising the News and UK Covid19 APIs in order to provide an always
up-to-date page where you can see case and news data about the pandemic. Stay informed, stay safe!

## Prerequisites

The Covid Dashboard was built with Python 3.9.9, make sure you're running this version to avoid potential issues! :)

## Installation

To install, start by cloning into this repository by using `git clone https://github.com/whoisEllie/ECM1400-Covid-Dashboard.git` (naturally, you will need
git installed for this to work).

Before you run the program, you'll need to install some dependancies using pip:
* `pip install uk-covid19`
* `pip install newsapi-python`
* `pip install Flask`

As you install the News API, make sure to grab an API Key! This goes into the `apiKey` field in `config.json`, which you'll notice is currently set to
`Your_API_Key_Here`

Now that that's completed, you can go ahead and run main.py, before heading to `127:0:0:1:5000` to see the locally hosted website. Congrats, you made it!

## Getting Started

With the site launched, you're free to start clicking around. You'll notice you're able to schedule updates, both for covid data and news data. Once you fill out a form and
submit it with the friendly-looking blue button, you'll notice data will refresh instantly, populating the form with a variety of friendly-looking widgets.

If you'd like to customize these widgets, your one-stop-shop is `config.json`. The categories are broken down below:

* `apiKey` - Your API key, as described above
* `title` - The title at the top of the Dashboard
* `image_path` - The path (within static/images) of the image/gif at the top
* `national_location` - The national location name
* `national_location_type` - The natonal location type for the Covid19 API
* `local_location` -  The local location name
* `local_location_type` - The local location type for the Covid19 API
* `max_articles` - The maximum amount of articles shown on the dasboard at once
* `search_terms` - The terms that the News API searches for articles with
* `blacklisted_strings` - Strings that are removed from article titles
* `news_language` - The language the news is served in
* `news_api_url` - The URL from which to fetch News API data
* `news_api_sortBy` - The sorting method to use with the news API
* `specify_sources` - Whether to specify sources or not (`true`/`false`)
* `sources` - If `specify_sources` is true, which sources to limit news to

## Testing

Testing is handled by integrated test modules & functions. The recommended means of testing is running pytest in the `/ECM1400-Covid-Dashboard` folder

You can install pytest with `pip install -U pytest`

## Developer Documentation

Documentation can be found at the accompanying ReadTheDocs page at https://ecm1400-covid-dashboard.readthedocs.io/en/latest/covid_data_handler.html, or by using the
docstrings in the program, which are used to generate the ReadTheDocs page

## Details

This program was written as a final Continuous Assessment (CA) for the ECM1400 course at the University of Exeter. index.html and accompanying frontend code was provided
by Matt Collison https://github.com/mcollison
