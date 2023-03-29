# Importing libraries
from datetime import date
from time import sleep

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from dataclasses import dataclass
from typing import Optional
import logging

from selenium.webdriver.common.by import By

from db import get_db


@dataclass
class Car:
    market: str
    brand: str
    model: str
    entity: str
    engine: str
    price: float
    horsepower: int
    bodystyle: str
    serie: str
    fuel: str
    consumption: float
    emission_co2: float
    transmission: str
    transmission_type: str
    driveline: str
    reaperstring: str
    matchstring: str
    datasource: str
    datum: str


url_base = "https://store.opel.fr"
url_start = url_base + '/configurable'


def get_models(driver):
    soup = make_soup(driver, url_start)
    car_models_links = set()

    # Finding all the div elements that contain car types
    outer = soup.find('div', id='skip-to-content')
    inner_divs = outer.find_all('div')

    for each in inner_divs:
        name_div = each.find('div', {'class': 'carTitleWrap'})
        if name_div is None: continue
        name = name_div.find('h2', {'class': 'carTitleWrap--link'}).get_text()
        link = name_div.find('a')['href']
        car_models_links.add((name, link))

    car_models_links = [model_and_link for model_and_link in car_models_links if all(model_and_link)]
    logging.info(f'Models found: {len(car_models_links)}')
    return car_models_links


def setup_driver():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver


def get_series(driver, models_and_links):
    series_found = list()
    for model, link in models_and_links:
        l = len(series_found)
        next_link = url_base + link
        soup = make_soup(driver, next_link)
        series_div = soup.findAll('div', {'class': 'trimContainer'})

        for each in series_div:
            series = each.find('h2')
            series_name = series.get_text()
            button_link = each.find('a')['href']
            series_found.append((model, series_name, button_link))
        # logging.info(f'Series for model {model}: {len(series_found)-l}') # over logging
    logging.info(f'Overall series found: {len(series_found)}')
    return series_found


def make_soup(driver, go_to_link=False, ):
    if go_to_link: driver.get(go_to_link)
    return BeautifulSoup(driver.page_source, 'html.parser')


def setup_my_logging():
    logging.basicConfig(filename='log', encoding='utf-8', level=logging.INFO,
                        format='%(asctime)s;%(levelname)s;%(message)s')


def insert_db(db, new_row):
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO car_db (market, brand, model, entity, engine, price, horsepower, bodystyle, serie, fuel, '
        'consumption, emission_co2, transmission, transmission_type, driveline, reaperstring, matchstring, '
        'datasource, datum) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        new_row)
    db.commit()
    cursor.close()


def read_car_data(model, series_name, soup, db):
    market = 'FR'
    brand = 'Opel'
    model = model

    bodystyle = "5D"
    serie = series_name
    fuel = soup.find('div', {'class': 'environmentalBlock'}) \
        .find('div', {'class': 'techWrapper'}) \
        .find('span').get_text()
    consumption = soup.find('div', {'data-testid': 'TESTING_TECH_INFO_CONSUMPTION'})
    if not consumption: consumption = soup.find('div', {'class': 'tech-point'}).find('strong')  # EV
    consumption = consumption.get_text().replace('*', '')

    emission_co2 = soup.find('div', {'class': 'emmisions-value'}).get_text().replace('*', '')
    transmission_helper = soup.find('span', {'class': 'technicalSubtitle'}).findAll('span')[-1].get_text().split()

    if 'boîte' in transmission_helper: transmission_helper = transmission_helper[1:]  # cut off boite
    if 'fixe' in transmission_helper: transmission_helper[1] = 'Fixe'  # fixed transmission

    transmission = "".join(transmission_helper[:2]).capitalize()
    transmission_type = transmission
    driveline = "FWD"
    datasource = 'configurator'
    datum = date.today().strftime('%Y-%m-%d')
    engine_helper = soup.find('button', {'class': 'engine isSelected'}).find('span',
                                                                             {'class': 'engineTitle'}).get_text()
    engine = engine_helper[:engine_helper.index('ch') - 1]
    price = soup.find('span', {'class': 'formatMoney'}).get_text().split()[0]
    hp_index = engine_helper.split().index('ch')
    horsepower = " ".join(engine_helper.split()[hp_index - 1:hp_index + 1])
    entity = f'{engine} {horsepower}'
    matchstring = ""
    reaperstring = f'{market}{brand}{model}{series_name}{engine}{horsepower}{transmission}{driveline}'.replace(' ', '')

    new_row = (market, brand, model, entity, engine, price, horsepower, bodystyle, serie, fuel, consumption,
               emission_co2, transmission, transmission_type, driveline, reaperstring, matchstring, datasource, datum)

    logging.info(reaperstring)

    insert_db(db, new_row)


def get_car_data(driver, valid_car_series, db):
    for model, series_name, link in valid_car_series:
        next_link = url_base + link
        soup = make_soup(driver, next_link)

        buttons = driver.find_elements(By.XPATH, "//button[@class='engine ']")

        read_car_data(model, series_name, soup, db)

        for each in buttons:
            each.click()
            soup = make_soup(driver)
            read_car_data(model, series_name, soup, db)


def main():
    setup_my_logging()
    driver = setup_driver()
    db = get_db()

    # Parsing the html with BeautifulSoup
    try:
        models_and_links = get_models(driver)
    except Exception as e:
        logging.critical('Unhandled error in get_models.', e)

    try:
        valid_car_series = get_series(driver, models_and_links)
    except Exception as e:
        logging.critical('Unhandled error in get_seres.', e)

    try:
        get_car_data(driver, valid_car_series, db)
    except Exception as e:
        logging.critical('Unhandled error in get_seres.', e)

    driver.close()


if __name__ == '__main__':
    main()
