import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from read_write_google_sheet import write_new_google_sheet_to_folder

# Setup Chrome
HEADLESS = True  # Change to False for debugging

options = Options()
options.add_argument("start-maximized")
if HEADLESS:
    options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")

# Disable images
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="137.0.7151.40").install()), options=options)
def total_turnover():
    try:
        url = "https://www.sharesansar.com/market-summary"
        driver.get(url)

        # Allow page to load
        time.sleep(1)

        # Locate the Total Turnover value
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table-bordered tbody tr")

        total_turnover = None
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 2 and "Total Turnovers" in cells[0].text:
                total_turnovers = cells[1].text
                total_turnover_value = float(total_turnovers.replace(",", ""))
                break

        return total_turnover_value

    finally:
        driver.quit()