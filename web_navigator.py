from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import urllib.parse
import time

def initialize_driver(viewport_width=1280, viewport_height=800):
    """Initializes and returns a Chrome WebDriver instance."""
    options = Options()
    options.add_argument(f"--window-size={viewport_width},{viewport_height}")
    # The following options are often useful for running in a headless environment
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox") # This can be necessary in some CI environments
    options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems
    driver = webdriver.Chrome(options=options)
    return driver

def search_web(driver, query):
    """Navigates to a Google search results page for the given query."""
    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"
    driver.get(search_url)
    # Optional: wait for a couple of seconds to observe the page
    # time.sleep(2)
    print(f"Navigated to: {search_url}") # For verification
    # In a real scenario, you'd return or process the page content here
    # For now, this function doesn't explicitly return anything.
    # The effect is that the driver instance will have the new page loaded.

def navigate_to_first_result(driver):
    """Navigates to the first organic search result link."""
    try:
        wait = WebDriverWait(driver, 10)
        # This XPATH attempts to find the first link (<a> tag) that has an <h3> child,
        # and is itself a descendant of a <div> with class 'tF2Cxc' or 'g'.
        # These classes are commonly used by Google for search result containers.
        first_result_link_element = wait.until(EC.presence_of_element_located((By.XPATH, '(//div[@class="tF2Cxc" or @class="g"]//a[h3])[1]')))
        
        url = first_result_link_element.get_attribute('href')
        
        if url:
            print(f"Navigating to first result: {url}")
            driver.get(url)
            # Optional: wait for page to load
            # time.sleep(2) 
            return url
        else:
            print("Could not extract href from the first search result link element.")
            return None
    except TimeoutException:
        print("Could not find the first search result link within the time limit.")
        return None
    except Exception as e:
        print(f"An error occurred while trying to navigate to the first result: {e}")
        return None
