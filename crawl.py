import time
import requests
import logging
from datetime import datetime,timedelta

from selenium import webdriver
from bs4 import BeautifulSoup


def calc_epl_date():
    '''
        경기가 시작한 날짜로 html tag에 접근하기 때문에 포맷에 맞춰 convert 해주는 함수
    '''

    now = datetime.now() - timedelta(5) # datetime.now() - timedelta(n) : 오늘부터 n만큼 이전의 날짜
    year = now.strftime("%Y")
    mon = now.strftime("%B")
    day_a = now.strftime("%A")
    day_d = now.strftime("%d")
    if day_d[0] == "0":
        day_d = day_d[1]
    
    return "{} {} {} {}".format(day_a, day_d, mon, year)

def set_chrome_driver():

    options = webdriver.ChromeOptions()

    options.add_argument("headless")
    options.add_argument("disable-gpu")

    return options

def main():

    epl_url = "https://www.premierleague.com/results"
    driver_path = "/home/limsh/project/python_mini_project/installation/chromedriver"
    driver_options = set_chrome_driver()

    # open chrome driver
    driver = webdriver.Chrome(driver_path, options=driver_options)
    driver.get(epl_url) # access premierleague by chromedriver 
    time.sleep(4) # wait for site loading

    html = driver.page_source # get html source

    soup = BeautifulSoup(html, "html.parser")
    match_day = calc_epl_date()
    
    match_list = soup.find("div", {"data-competition-matches-list" : match_day})
    if match_list is None:
        exit()
    match_list = match_list.find_all("li", {"class" : "matchFixtureContainer"})
    
    match_result = dict()

    for match in match_list:
        match_link = match.find_all("div", {"class" : "fixture postMatch", "data-template-rendered" : ""})[0]
        match_id = match_link.attrs["data-matchid"]
        match_detail = "https://www.premierleague.com/match/" + match_id
        try:
            res = requests.get(match_detail)
        except Exception as ex:
            logging.error("Request Error : {}".format(ex))
            continue
        match_html = res.text
        match_soup = BeautifulSoup(match_html, "html.parser")
        match_title = match_soup.find("title").get_text()
        match_score = match_soup.find("div", {"class" : "score fullTime"}).get_text()
        match_result[match_title] = match_score

    driver.quit() # close chrome driver

    return match_result

if __name__ == "__main__": 

    print(main())