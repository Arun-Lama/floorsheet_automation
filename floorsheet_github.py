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

# Setup Chrome in headless mode
options = Options()
options.add_argument("start-maximized")
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--no-sandbox")  # Bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
options.add_argument("window-size=1920,1080")  # Set the window size for consistency

options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
)

# Disable images
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)
time.sleep(2)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="137.0.7151.40").install()), options=options)


# Track time
start_time = time.time()

# Visit target URL
url = "https://nepalstock.com.np/floor-sheet"
driver.get(url)
time.sleep(5)
driver.save_screenshot("headless_debug5.png")

# Set limit to 500
WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/main/div/app-floor-sheet/div/div[3]/div/div[5]/div/select/option[6]"))
).click()

# Click Filter
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/main/div/app-floor-sheet/div/div[3]/div/div[6]/button[1]"))
).click()
time.sleep(0.5)
# Wait for table rows to load
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, ".table-responsive tbody tr"))
)
# driver.save_screenshot("headless_debug5.png")

# Start scraping
all_data = []
seen_contracts = set()
page_no = 1

while True:
    print(f"Scraping page {page_no}...")

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".table-responsive tbody tr"))
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        rows = soup.select(".table-responsive tbody tr")

        # Capture current page's first contractNo
        if not rows:
            print("No rows found, skipping.")
            break
        first_row_text = rows[0].text.strip()

        new_rows_added = 0
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 8:
                contract_no = cols[1].get_text(strip=True)
                if contract_no in seen_contracts:
                    continue
                seen_contracts.add(contract_no)

                data = {
                    "contractNo": contract_no,
                    "stockSymbol": cols[2].get_text(strip=True),
                    "buyer": cols[3].get_text(strip=True),
                    "seller": cols[4].get_text(strip=True),
                    "quantity": int(cols[5].get_text(strip=True).replace(",", "")),
                    "rate": float(cols[6].get_text(strip=True).replace(",", "")),
                    "amount": float(cols[7].get_text(strip=True).replace(",", "")),
                }
                all_data.append(data)
                new_rows_added += 1

        print(f"Added {new_rows_added} new rows.")

        # Check for Next button
        try:
            next_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.pagination-next"))
            )

            if "disabled" in next_btn.get_attribute("class"):
                print("Next button is disabled. Finished scraping.")
                break

            next_link = next_btn.find_element(By.TAG_NAME, "a")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
            next_link.click()
            time.sleep(1)
            # Wait for the new page's first row to be different
            WebDriverWait(driver, 20).until(
                lambda d: BeautifulSoup(d.page_source, "html.parser").select(".table-responsive tbody tr")[0].text.strip() != first_row_text
            )

            page_no += 1

        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
            print("No more pages or error encountered while clicking next.")
            break

    except Exception as e:
        print("Error during scraping:", e)
        break

# Close browser
driver.quit()

# Save data to DataFrame
df = pd.DataFrame(all_data)
print(f"Scraped {len(df)} unique rows.")

# Save to CSV (optional)
# df.to_csv("floorsheet_data.csv", index=False)

# Total time taken
end_time = time.time()
print(f"Total runtime: {round(end_time - start_time, 2)} seconds")