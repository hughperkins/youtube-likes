import time
from os.path import expanduser as expand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


url = "http://youtube.com"
webdriver_path = expand("~/Downloads/chromedriver")
service_url = 'http://127.0.0.1:9515'

# service = Service(webdriver_path)
# print('service', service)
# service.start()
# print('service', service)
# print('service.service_url', service.service_url)
driver = webdriver.Remote(service_url)
print('driver', driver)
driver.get(url)
time.sleep(5)  # Let the user actually see something!
driver.quit()
