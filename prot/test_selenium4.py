import time
from os.path import expanduser as expand
from selenium import webdriver

webdriver_path = expand("~/Downloads/chromedriver")
# url = "http://youtube.com"
url = "http://www.google.com"

options = webdriver.ChromeOptions()
# options.binary_location = webdriver_path
# options.
driver = webdriver.Chrome(options=options)
# service=webdriver_path)  # Optional argument, if not specified will search path.
driver.get(url)
time.sleep(5)  # Let the user actually see something!
search_box = driver.find_element_by_name('q')
search_box.send_keys('ChromeDriver')
search_box.submit()
time.sleep(5)  # Let the user actually see something!
driver.quit()
