import time
from os.path import expanduser as expand
from selenium import webdriver
from selenium.webdriver.common.by import By

# URL of the page to check
url = "http://youtube.com"

# Path to your WebDriver executable (e.g., ChromeDriver)
webdriver_path = expand("~/Downloads/chromedriver")

# Initialize the WebDriver (this example uses Chrome)
driver = webdriver.Chrome(executable_path=webdriver_path)

# Open the URL
driver.get(url)

try:
    while True:
        # Find all <h1> elements on the page
        h1_elements = driver.find_elements(By.TAG_NAME, 'h1')
        
        # Count the number of <h1> tags
        h1_count = len(h1_elements)
        
        # Print the count
        print(f"Number of <h1> tags: {h1_count}")
        
        # Wait for 1 minute (60 seconds)
        time.sleep(60)

except KeyboardInterrupt:
    # If the script is interrupted, close the WebDriver
    print("Script interrupted by user. Closing WebDriver.")
    driver.quit()
except Exception as e:
    # Print any other exceptions
    print(f"An error occurred: {e}")
    driver.quit()
