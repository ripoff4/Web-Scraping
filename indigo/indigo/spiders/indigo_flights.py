import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector


class IndigoFlightsSpider(scrapy.Spider):
    name = "indigo_flights"
    allowed_domains = ["www.goindigo.in"]
    start_urls = ["https://www.goindigo.in/domestic-flights.html"]

    def __init__(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("disable-blink-features=AutomationControlled")
        options.add_argument("--window-size=1920,1080")
        path=r'C:\Users\tejva\Downloads\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe'
        self.driver = webdriver.Chrome(service=Service(path),options=options)

    def parse(self, response):
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[h2[contains(normalize-space(.), 'Most searched flights')]]"))
            )
        except Exception as e:
            self.logger.error(f"Timeout waiting for flights: {e}")
            return
        sel = Selector(text=self.driver.page_source)
        container = sel.xpath("//div[h2[contains(normalize-space(.), 'Most searched flights')]]")
        for elements in container:
            li_element = elements.xpath(".//ul/li")
            for li in li_element:
                link = li.xpath("./a/@href").get()
                if link:
                    yield response.follow(link, callback=self.parse_flights)

    def parse_flights(self, response):
        self.driver.get(response.url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"faretable-body")]'))
            )
        except Exception as e:
            self.logger.error(f"Timeout waiting for flight data: {e}")
            return
        sel = Selector(text=self.driver.page_source)
        flights = sel.xpath('//div[contains(@class,"faretable-body")]')

        for flight in flights:
            yield {
                "flight_departuredate": flight.xpath('.//div[contains(@class, "faretable-date")]/@data-date').get(),
                "flight_arrivaldate": flight.xpath('.//div[contains(@class, "faretable-arrival-date")]/@data-date').get(),
                "flight_timings": flight.xpath('.//div[contains(@class, "faretable-deptime")]/text()').get(),
                "flight_fare": flight.xpath('.//span[contains(@class,"lowest-fare")]/text()').get(),
            }
    def closed(self,reason):
        self.driver.quit()
