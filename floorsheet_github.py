import os 

key_base64 = os.environ["GCP_SA_KEY_BASE64"]
print(key_base64)
# import time
# import pandas as pd
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
# from webdriver_manager.chrome import ChromeDriverManager
# from read_write_google_sheet import write_new_google_sheet_to_folder
# import total_traded_shares

# # Setup Chrome
# HEADLESS = True  # Change to False for debugging

# options = Options()
# options.add_argument("start-maximized")
# if HEADLESS:
#     options.add_argument("--headless")
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("window-size=1920,1080")
# options.add_argument("--remote-debugging-port=9222")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")

# # Disable images
# prefs = {"profile.managed_default_content_settings.images": 2}
# options.add_experimental_option("prefs", prefs)

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# # driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="137.0.7151.40").install()), options=options)
# # Track time
# start_time = time.time()

# # Visit target URL
# url = "https://nepalstock.com.np/floor-sheet"
# driver.get(url)
# time.sleep(2)

# # Set limit to 500
# WebDriverWait(driver, 15).until(
#     EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/main/div/app-floor-sheet/div/div[3]/div/div[5]/div/select/option[6]"))
# ).click()

# # Click Filter
# WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/div/main/div/app-floor-sheet/div/div[3]/div/div[6]/button[1]"))
# ).click()

# time.sleep(2)

# # Start scraping
# all_data = []
# seen_contracts = set()
# page_no = 1

# while True:
#     print(f"Scraping page {page_no}...")

#     try:
#         WebDriverWait(driver, 10).until(
#             EC.visibility_of_element_located((By.CSS_SELECTOR, ".table-responsive tbody tr"))
#         )

#         # Retry logic if rows are missing
#         MAX_RETRIES = 3
#         retry_count = 0
#         rows = []

#         while retry_count < MAX_RETRIES:
#             soup = BeautifulSoup(driver.page_source, "html.parser")
#             rows = soup.select(".table-responsive tbody tr")
#             if rows:
#                 break
#             print(f"No rows found. Retrying... ({retry_count + 1}/{MAX_RETRIES})")
#             time.sleep(2)
#             retry_count += 1

#         if not rows:
#             print("No rows found after retries. Saving HTML for debugging and exiting.")
#             with open("debug_empty_rows.html", "w", encoding="utf-8") as f:
#                 f.write(driver.page_source)
#             break

#         first_row_text = rows[0].text.strip()
#         new_rows_added = 0

#         for row in rows:
#             cols = row.find_all("td")
#             if len(cols) >= 8:
#                 contract_no = cols[1].get_text(strip=True)
#                 if contract_no in seen_contracts:
#                     continue
#                 seen_contracts.add(contract_no)

#                 data = {
#                     "Contract No.": contract_no,
#                     "Stock Symbol": cols[2].get_text(strip=True),
#                     "Buyer": cols[3].get_text(strip=True),
#                     "Seller": cols[4].get_text(strip=True),
#                     "Quantity": int(cols[5].get_text(strip=True).replace(",", "")),
#                     "Rate (Rs)": float(cols[6].get_text(strip=True).replace(",", "")),
#                     "Amount (Rs)": float(cols[7].get_text(strip=True).replace(",", "")),
#                 }
#                 all_data.append(data)
#                 new_rows_added += 1

#         print(f"Added {new_rows_added} new rows.")

#         # Check for Next button
#         try:
#             next_btn = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "li.pagination-next"))
#             )

#             if "disabled" in next_btn.get_attribute("class"):
#                 print("Next button is disabled. Finished scraping.")
#                 break

#             driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)

#             next_link = next_btn.find_element(By.TAG_NAME, "a")
#             WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "a")))
#             next_link.click()
#             time.sleep(2)

#             # Wait for the new page to load (detect change in first row)
#             WebDriverWait(driver, 20).until(
#                 lambda d: BeautifulSoup(d.page_source, "html.parser").select(".table-responsive tbody tr")[0].text.strip() != first_row_text
#             )

#             page_no += 1

#         except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
#             print("No more pages or error encountered while clicking next.")
#             break

#     except Exception as e:
#         print("Error during scraping:", e)
#         break

# # Close browser
# driver.quit()
# # Time taken
# end_time = time.time()
# print(f"Total runtime: {round(end_time - start_time, 2)} seconds")
# df = pd.DataFrame(all_data)
# date = str(df['Contract No.'].iloc[-1])[:8]
# date_format = pd.to_datetime(date, format='%Y%m%d').strftime('%Y-%m-%d')
# df["Date"] = date_format
# df["Contract No."] = "'" + df["Contract No."].astype(str)
# print(f"Scraped {len(df)} unique rows.")

# total_traded_turnover= total_traded_shares.total_turnover()


# if total_traded_turnover != df["Amount (Rs)"].sum():
#     print("Wrong Data!")
#     print(total_traded_turnover,  df["Amount (Rs)"].sum())
# else: 
#     print('Correct Data Downloaded')
#     print(f'Correct total turnover = {total_traded_turnover}')
#     write_new_google_sheet_to_folder(df, f"{date_format} floorsheet", "1U3MOR0IMKuq30c-B9abSV-eeljjpUXPC")
