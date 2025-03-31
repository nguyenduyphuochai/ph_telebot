import os
import requests
from bs4 import BeautifulSoup
import json
import time
import schedule
from telegram import Bot

# Get credentials from Railway environment variables
BOT_TOKEN = os.getenv("8192269061:AAHerPSYVwOh4JIpkpEJ7UFV-QLBXbpyhlY")
CHAT_ID = os.getenv("ph_2handlandbot")

# URL to scrape
URL = "https://2handland.com/muon-mua"
CATEGORIES = ["Máy chơi game cũ", "Phụ kiện cũ"]

# Load previous listings
try:
    with open("listings.json", "r") as file:
        previous_listings = json.load(file)
except FileNotFoundError:
    previous_listings = []

bot = Bot(token=BOT_TOKEN)

def scrape_listings():
    global previous_listings
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    new_listings = []
    
    for item in soup.select(".product-item"):  # Adjust selector if necessary
        title = item.select_one(".product-title").text.strip()
        category = item.select_one(".product-category").text.strip()
        price = item.select_one(".product-price").text.strip()
        link = item.select_one("a")["href"]
        image = item.select_one("img")["src"]

        if category in CATEGORIES:
            listing = {"title": title, "category": category, "price": price, "link": link, "image": image}
            new_listings.append(listing)

    # Check for new listings
    new_items = [item for item in new_listings if item not in previous_listings]
    if new_items:
        for item in new_items:
            message = f"📢 *New Listing: {item['title']}*\n🏷 *Category:* {item['category']}\n💰 *Price:* {item['price']}\n🔗 [View Listing]({item['link']})"
            bot.send_photo(chat_id=CHAT_ID, photo=item["image"], caption=message, parse_mode="Markdown")
        
        # Update previous listings
        previous_listings = new_listings
        with open("listings.json", "w") as file:
            json.dump(previous_listings, file)

# Schedule the bot to run every 10 minutes
schedule.every(10).minutes.do(scrape_listings)

if __name__ == "__main__":
    print("Bot is running...")
    while True:
        schedule.run_pending()
        time.sleep(60)
