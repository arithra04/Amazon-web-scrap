from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Initialize Selenium WebDriver
def init_driver():
    options = Options()
    options.set_preference(
        "general.useragent.override",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    return driver

# Scrape Amazon products
def scrape_amazon(search_query):
    driver = init_driver()
    amazon_url = f"https://www.amazon.in/s?k={search_query.replace(' ', '+')}"
    driver.get(amazon_url)
    time.sleep(3)  # Allow the page to load

    # Parse the page source using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Extract product details
    products = []
    for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
        # Safely extract product name
        product_name = item.h2.text.strip() if item.h2 else "N/A"

        # Safely extract price
        price = item.find('span', 'a-price-whole')
        price = price.text.strip() if price else "N/A"

        # Safely extract rating
        rating = item.find('span', 'a-icon-alt')
        rating = rating.text.strip() if rating else "N/A"

        # Safely extract product link
        link_tag = item.find('a', {'class': 'a-link-normal s-no-outline'})
        full_link = f"https://www.amazon.in{link_tag['href']}" if link_tag and link_tag.has_attr('href') else "N/A"

        # Safely extract product image URL
        image_tag = item.find('img', {'class': 's-image'})
        image_url = image_tag['src'] if image_tag else "N/A"

        # Append the product data
        products.append({
            "Product Name": product_name,
            "Price": price,
            "Rating": rating,
            "Link": full_link,
            "Image URL": image_url
        })

    return products

# Save data to a CSV file
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Main Function
if __name__ == "__main__":
    search_term = input("Enter the product to search on Amazon: ")
    print("Scraping data, please wait...")
    results = scrape_amazon(search_term)

    if results:
        save_to_csv(results, "amazon_products.csv")
        print("Scraping completed successfully! Check the amazon_products.csv file for the results.")
    else:
        print("No products found or an error occurred.")
