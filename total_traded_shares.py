def get_total_tradedshares():
    import re
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # Set up Chrome options
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--no-sandbox")  # Needed in CI
    options.add_argument("--disable-dev-shm-usage")  # Prevents crashes in limited-memory environments
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")  # Ensure consistent layout
    options.add_argument("--enable-javascript")  # Just in case
    
    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://nepalstock.com.np")
        
        # Wait for the specific content area to load (not the tag name)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(text(),'Total Traded Shares')]/following-sibling::div/span[2]"
            ))
        )

        # Extra sleep to ensure JS loads fully (because Angular is lazy-loaded)
        time.sleep(5)

        # Now grab the span
        span = driver.find_element(
            By.XPATH,
            "//div[contains(text(),'Total Traded Shares')]/following-sibling::div/span[2]"
        )

        text = span.text
        print(f"[Debug] Span text: {text}")

        match = re.search(r'([\d,]+)', text)
        if match:
            number_str = match.group(1).replace(",", "")
            volume = int(number_str)
            return volume
        else:
            print("Could not find number in text.")
            return None

    finally:
        driver.quit()

# Run the function
print(get_total_tradedshares())
