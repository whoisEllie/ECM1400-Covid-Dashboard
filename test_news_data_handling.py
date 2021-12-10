from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import calculate_interval
def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news('test')

def test_calculate_interval():
    interval = calculate_interval()
    assert interval == 1639180800.0