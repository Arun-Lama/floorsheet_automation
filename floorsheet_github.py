# Working Good.
import os
import time
import pandas as pd
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
from read_write_google_sheet import write_new_google_sheet_to_folder
from total_traded_shares import get_total_tradedshares


# Print current date and time
print(datetime.datetime.now())

# Set the URL and output file path
base_url = "https://nepalstock.com/floor-sheet?&symbol=&floor=1&startDate=&endDate=&_limit="


# Set up Selenium WebDriver with Chrome options
options = Options()
options.add_argument("--headless")  # required
options.headless = True  # Enable headless mode
driver = webdriver.Chrome(options=options)

# Open the webpage
driver.get(base_url)

# Set limit
select_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/div/main/div/app-floor-sheet/div/div[3]/div/div[5]/div/select/option[6]"))
)
select_element.click()
limit_set = select_element.text
print("Set Limit =", limit_set)

# Click Filter button
filter_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/main/div/app-floor-sheet/div/div[3]/div/div[6]/button[1]"))
)
filter_button.click()
time.sleep(1.5)  # Wait for the page to load

# Extract number of pages
try:
    num_pages_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/app-root/div/main/div/app-floor-sheet/div/div[5]/div[2]/pagination-controls/pagination-template/ul/li[9]/a/span[2]'))
    )
    num_pages = int(num_pages_element.text)
except:
    # In case the XPath is still incorrect or changes, print an error and set a default value for number of pages
    print("Could not locate the number of pages element.")
    num_pages = 1  # Default to 1 page if unable to determine the actual number
print("Number of Pages =", num_pages)

# Initialize an empty list to store all the pages' data
all_floorsheet_data = []

# Loop through pages and extract data
for page in range(1, num_pages + 1):
    # Extract the table data using Pandas
    dfs = pd.read_html(StringIO(driver.page_source))
    floorsheet_data = dfs[0]

    # Append the current page's data to the overall data list
    all_floorsheet_data.append(floorsheet_data)
    print("Page:", page)
# Navigate to the next page if not on the last page
    if page < num_pages:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/main/div/app-floor-sheet/div/div[5]/div[2]/pagination-controls/pagination-template/ul/li[10]/a"))
        )
        next_button.click()
        time.sleep(1.5)  # Wait for the page to load

driver.quit()


# Concatenate the dataframes in the list into a single dataframe
all_data = pd.concat(all_floorsheet_data, ignore_index=True)
date = str(all_data['Contract No.'].iloc[-1])[:8]
date_format = pd.to_datetime(date, format='%Y%m%d').strftime('%Y-%m-%d')
all_data["Date"] = date_format
all_data["Contract No."] = "'" + all_data["Contract No."].astype(str)

# total_shares= get_total_tradedshares()


# if total_shares != all_data["Quantity"].sum():
#     print("Wrong Data!")
# else: 
#     print('Correct Data Downloaded')
#     print(f'Correct total trades shares = {total_shares}')
write_new_google_sheet_to_folder(all_data, f"{date_format} floorsheet", "1U3MOR0IMKuq30c-B9abSV-eeljjpUXPC")

