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
import total_traded_shares

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
options.add_argument("--log-level=3")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Track time
start_time = time.time()

# Visit target URL
url = "https://nepalstock.com.np/floor-sheet"
driver.get(url)

# Set rows per page to 500
WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.XPATH, "//select/option[@value='500']"))
).click()

# Click Filter
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Filter')]"))
).click()

# Start scraping
all_data = []
seen_contracts = set()
page_no = 1
MAX_RETRIES = 5

while True:
    for attempt in range(1, MAX_RETRIES + 1):
        loop_start = time.time()
        print(f"Scraping page {page_no}... (Attempt {attempt})")

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".table-responsive tbody tr"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            rows = soup.select(".table-responsive tbody tr")

            if not rows:
                print("No rows found. Retrying...")
                time.sleep(2)
                continue

            new_rows_added = 0
            filtered_rows = []

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 8:
                    contract_no = cols[1].get_text(strip=True)
                    if contract_no in seen_contracts:
                        continue
                    seen_contracts.add(contract_no)
                    filtered_rows.append(row)

                    data = {
                        "Contract No.": contract_no,
                        "Stock Symbol": cols[2].get_text(strip=True),
                        "Buyer": cols[3].get_text(strip=True),
                        "Seller": cols[4].get_text(strip=True),
                        "Quantity": int(cols[5].get_text(strip=True).replace(",", "")),
                        "Rate (Rs)": float(cols[6].get_text(strip=True).replace(",", "")),
                        "Amount (Rs)": float(cols[7].get_text(strip=True).replace(",", "")),
                    }
                    all_data.append(data)
                    new_rows_added += 1

            first_row_text = filtered_rows[0].text.strip() if filtered_rows else ""

            # Check if last page
            is_last_page = False
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "li.pagination-next")
                if "disabled" in next_btn.get_attribute("class"):
                    is_last_page = True
            except NoSuchElementException:
                is_last_page = True

            if not is_last_page and new_rows_added < 500:
                print(f"Only {new_rows_added} rows found. Retrying page...")
                time.sleep(2)
                continue

            print(f"Added {new_rows_added} new rows.")
            print(f"Page {page_no} took {round(time.time() - loop_start, 2)} seconds.")

            if is_last_page:
                print("Next button is disabled. Finished scraping.")
                break

            # Click next
            driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
            next_link = next_btn.find_element(By.TAG_NAME, "a")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
            next_link.click()

            # Wait for new page
            WebDriverWait(driver, 20).until(
                lambda d: BeautifulSoup(d.page_source, "html.parser").select(".table-responsive tbody tr")[0].text.strip() != first_row_text
            )

            page_no += 1
            break

        except Exception as e:
            print(f"Error on page {page_no} (Attempt {attempt}): {e}")
            time.sleep(2)
            if attempt == MAX_RETRIES:
                print("Max retries reached. Exiting.")
                break
    else:
        break

# Close browser
driver.quit()

# Time taken
end_time = time.time()
print(f"Total runtime: {round(end_time - start_time, 2)} seconds")

# Convert to DataFrame
df = pd.DataFrame(all_data)

# Format date
date = str(df['Contract No.'].iloc[-1])[:8]
date_format = pd.to_datetime(date, format='%Y%m%d').strftime('%Y-%m-%d')
df["Date"] = date_format
df["Contract No."] = "'" + df["Contract No."].astype(str)

print(f"Scraped {len(df)} unique rows.")

# Check with total turnover
total_traded_turnover = total_traded_shares.total_turnover()

if total_traded_turnover != df["Amount (Rs)"].sum():
    print("Wrong Data!")
    print(total_traded_turnover, df["Amount (Rs)"].sum())
else:
    print("Correct Data Downloaded")
    print(f"Correct total turnover = {total_traded_turnover}")
    write_new_google_sheet_to_folder(df, f"{date_format} floorsheet", "1U3MOR0IMKuq30c-B9abSV-eeljjpUXPC")
