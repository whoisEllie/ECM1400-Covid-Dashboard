from re import I
from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_data_handler import is_integer
from covid_data_handler import find_recent_value
from covid_data_handler import sum_recent_values
from covid_data_handler import dict_to_csv
from covid_data_handler import calculate_interval

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')

def test_is_integer():
    result = is_integer(10)
    assert result == True

def test_find_recent_value():
    result = find_recent_value(parse_csv_data('nation_2021-10-28.csv'), "hospitalCases")
    assert result == 7_019

def test_sum_recent_values():
    result = sum_recent_values(parse_csv_data('nation_2021-10-28.csv'), "newCasesBySpecimenDate", 7)
    assert result == 240_299

def test_dict_to_csv():
    dict_to_csv(covid_API_request())

def test_calculate_interval():
    interval = calculate_interval()
    assert interval == 1639180800.0