from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import requests
import os


def set_chrome_options() -> Options:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    options = webdriver.ChromeOptions()
    # options.add_experimental_option("detach", True)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=dbus")

    return options


if __name__ == "__main__":
    driver = webdriver.Chrome(options=set_chrome_options())

    driver.get("https://finance.yahoo.com/most-active/")

    backend_url = os.environ.get("BACKEND_URL", "localhost:5432")
    frontend_url = os.environ.get("FRONTEND_URL", "localhost:5432")

    # Bypass cookies
    driver.find_element("xpath", "//*[@id=\"scroll-down-btn\"]").click()
    sleep(2)
    driver.find_element("xpath", "//*[@id=\"consent-page\"]/div/div/div/form/div[2]/div[2]/button[1]").click()

    sleep(5)

    driver.find_element("xpath", "//*[@id=\"scr-res-table\"]/div[2]/span/div").click()
    show_rows = driver.find_element("xpath", "//*[@id=\"scr-res-table\"]/div[2]/span/div[2]").find_elements("xpath",
                                                                                                            "*")
    show_rows[len(show_rows) - 1].click()  # expand all stocks
    sleep(3)
    field_names = ['Company Name', 'Company Abvr', 'Price']
    while True:
        prices = []
        for i in range(1, 99):
            try:
                priceElement = driver.find_element("xpath", "//*[@id=\"scr-res-table\"]/div[1]/table/tbody/tr[" + str(
                    i) + "]/td[3]")
                price = float(priceElement.find_elements("xpath", "*")[0].text)
                # sleep(0.5)
                companyName = driver.find_element("xpath", "//*[@id=\"scr-res-table\"]/div[1]/table/tbody/tr[" + str(
                    i) + "]/td[2]")
                # sleep(0.5)
                companyAbvr = driver.find_element("xpath", "//*[@id=\"scr-res-table\"]/div[1]/table/tbody/tr[" + str(
                    i) + "]/td[1]/a")
                # sleep(0.5)
                print(
                    companyAbvr.text + " " + companyName.text + " " + priceElement.find_elements("xpath", "*")[0].text)
                d = {'Company Name': companyName.text, 'Company Abvr': companyAbvr.text, 'Price': price}
                prices.append(d)
            except Exception as e:
                print("Exception at " + str(i))
                print(e)

        prices_json = json.dumps(prices, indent=4)
        prices_json = prices_json.encode()
        print(prices_json)

        try:
            r = requests.post(url=backend_url, data=prices_json)
            print("Status code", r.status_code)
            print("Response", r.text)
        except Exception as e:
            print(e)
