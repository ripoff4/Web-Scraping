import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

website = 'https://www.amazon.in/'
path = r'C:\Users\tejva\Downloads\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe'

service = Service(path)
options = Options()
options.add_argument("--disable-popup-blocking")

driver = webdriver.Chrome(service=service, options=options)
driver.get(website)

product = []
price = []

try:
    # Handle CAPTCHA if present
    try:
        captcha = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//input[contains(@id,"captchacharacters")]'))
        )
        driver.execute_script("arguments[0].scrollIntoView();", captcha)

        print("CAPTCHA detected! Please enter it manually.")
        captcha_text = input("Enter CAPTCHA manually: ")
        captcha.clear()
        captcha.send_keys(captcha_text)

        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button'))
        )

        driver.execute_script("arguments[0].click();", submit_button)
        time.sleep(3)

        print("CAPTCHA submitted successfully!")
    except Exception:
        print("No CAPTCHA found. Continuing...")

    print("Proceeding with further automation...")

    # Search for "mobile phones"
    Searchbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "twotabsearchtextbox"))
    )
    Searchbox.send_keys('mobile phones')

    searchbutton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[contains(@id,"nav-search-submit-button")]'))
    )
    driver.execute_script("arguments[0].click();", searchbutton)

    while True:
        time.sleep(random.randint(3, 6))  # Prevent bot detection

        # Extract products from the current page
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@data-component-type="s-search-result"]'))
        )

        for products in container:
            # Extract product title
            product_title_elements = products.find_elements(By.XPATH, './/a/h2/span')
            if product_title_elements:
                product_title_text = product_title_elements[0].text.strip()
                product.append(product_title_text)

            # Extract product price
            product_price_elements = products.find_elements(By.XPATH, './/span[@class="a-price-whole"]')
            if product_price_elements:
                product_price_text = product_price_elements[0].text.strip()
                price.append(product_price_text)
            else:
                price.append("N/A")  # If no price, append "N/A" to keep lists aligned

        # Try to find and click the "Next" button
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(@aria-label,"Go to next page")]'))
            )
            driver.execute_script("arguments[0].click();", next_button)
        except Exception:
            print("No more pages. Scraping complete.")
            break  # No next button found, exit loop

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()

# Create DataFrame and save to CSV
df = pd.DataFrame({'Product': product, 'Price': price})
df.to_csv('Amazon.csv', index=False)

print("Scraping completed. Data saved to Amazon.csv.")
