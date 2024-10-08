
                    
import requests
import asyncio
import nest_asyncio
from bs4 import BeautifulSoup
from telegram.helpers import escape_markdown
from telegram import Bot
import logging
# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# Telegram Bot Token
TOKEN = '7893336962:AAE-CWOXuwE9nlU5pJZRNoTMJBusWBPyuVk'

# Chat ID to send notifications to
CHAT_ID = '6246129018'
# Initialize Telegram bot
bot = Bot(token=TOKEN)

# Store previously seen project URLs to detect new projects
previous_projects = set()

# Function to scrape Mostaql projects
def scrape_mostaql_projects():
    # Define the URL
    URL = 'https://mostaql.com/projects?category=development&budget_max=10000&sort=latest'

    # Define the headers
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'mostaql.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
        'Cookie':'XSRF-TOKEN=eyJpdiI6Ik1mRGR0dHRiZzc3aTRHUDMwd1VjdVE9PSIsInZhbHVlIjoiSlZYTEVxdkxpNldvVXFQeVlMQm9MOWdDUkl0RmdOWVIvMUpreENRNUxzWTFpRzVqbEx2Qjd2bVBsWEpJcXc2RGR6cGNqUjNpVUNrakkzbGpNSFZ1OHdlUVBFUWZEbHlxNXpPNS9hb1hwV0NINVpzZ3p1dEx1UHlUQi9sQ3JkcFEiLCJtYWMiOiIzODg2ZmZmNmVlYTc4YzgzMTY1MWZiMWRmMGMxMmIxZjZlNjhkNDA3YjFmZDAyYzgwOWMxODYyMjI3MGQzZTA1IiwidGFnIjoiIn0%3D; mostaqlweb=eyJpdiI6IllMa0RuQmhlc3NOblRHdGFNMEhoR1E9PSIsInZhbHVlIjoibHpRNndXWS93cjlUelJVanB0NURlcExDU3ZmQ1RNZDJOa1FxOUtsbVFxaFZNUTJzekk0UnJqejM3ZkVZekp0eTVvWGlTUkxyRm9xTWQxeVlRS2U0blMxMEdaUFRIdEhrME5oOXdRRmpuTndnUllVMGJ4MERSVndid09ZZTd2aVQiLCJtYWMiOiIwNGY1NzlmMDZkYmI1NzQyNjE2MjdiZGUzYTRlODY2NmZjZjljYzgzZDY2YjcxZjMyY2Q4ZGQ3ZGM0YThkYTg1IiwidGFnIjoiIn0%3D'
    }

    # Define the cookies
    cookies = {
        'XSRF-TOKEN': 'eyJpdiI6Ik1mRGR0dHRiZzc3aTRHUDMwd1VjdVE9PSIsInZhbHVlIjoiSlZYTEVxdkxpNldvVXFQeVlMQm9MOWdDUkl0RmdOWVIvMUpreENRNUxzWTFpRzVqbEx2Qjd2bVBsWEpJcXc2RGR6cGNqUjNpVUNrakkzbGpNSFZ1OHdlUVBFUWZEbHlxNXpPNS9hb1hwV0NINVpzZ3p1dEx1UHlUQi9sQ3JkcFEiLCJtYWMiOiIzODg2ZmZmNmVlYTc4YzgzMTY1MWZiMWRmMGMxMmIxZjZlNjhkNDA3YjFmZDAyYzgwOWMxODYyMjI3MGQzZTA1IiwidGFnIjoiIn0=',  # Replace with actual token
        'mostaqlweb': 'eyJpdiI6IllMa0RuQmhlc3NOblRHdGFNMEhoR1E9PSIsInZhbHVlIjoibHpRNndXWS93cjlUelJVanB0NURlcExDU3ZmQ1RNZDJOa1FxOUtsbVFxaFZNUTJzekk0UnJqejM3ZkVZekp0eTVvWGlTUkxyRm9xTWQxeVlRS2U0blMxMEdaUFRIdEhrME5oOXdRRmpuTndnUllVMGJ4MERSVndid09ZZTd2aVQiLCJtYWMiOiIwNGY1NzlmMDZkYmI1NzQyNjE2MjdiZGUzYTRlODY2NmZjZjljYzgzZDY2YjcxZjMyY2Q4ZGQ3ZGM0YThkYTg1IiwidGFnIjoiIn0='  # Replace with actual value
    }

    # Send the GET request with headers and cookies
    response = requests.get(URL, headers=headers, cookies=cookies)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        projects = []
        
        for project in soup.find_all('tr', class_='project-row'):
            title_elem = project.find('h2', class_='mrg--bt-reset')
            if title_elem and title_elem.find('a'):
                title = title_elem.find('a').text.strip()
                link = title_elem.find('a')['href']
                
                time_elem = project.find('time')
                time_text = time_elem.text.strip() if time_elem else "Unknown time"
                
                offers_elem = project.find('i', class_='fa fa-fw fa-ticket')
                offers_text = offers_elem.find_next('li').text.strip() if offers_elem else "Unknown offers"
                
                projects.append((title, link, time_text, offers_text))
        
        return projects
    else:
        logger.error(f"Failed to fetch projects. Status code: {response.status_code}")
        return []

async def check_for_new_projects():
    global previous_projects
    
    projects = scrape_mostaql_projects()
    
    new_projects = [(title, url, time, offers) for title, url, time, offers in projects if url not in previous_projects]
    for title, url, time, offers in new_projects:
        message = (f"New Project: {title}\n"
                   f"Time: {time}\n"
                #    f"Offers: {offers}\n"
                   f"Link: {url}")
        await bot.send_message(chat_id=CHAT_ID, text=message)
    # for title, url, time, offers in new_projects:
    #     url_link = f"[Click here]({escape_markdown(url)})"
    #     message = (f"Title: {escape_markdown(title)}\n"
    #                f"Time: {escape_markdown(time)}\n"
    #             #    f"Offers: {offers}\n"
    #                f"Link: {escape_markdown(url_link)}")
    #     await bot.send_message(chat_id=CHAT_ID, text=escape_markdown(message),   parse_mode='MarkdownV2',)
    
    previous_projects.update([url for _, url, _, _ in projects])

async def main_loop():
    while True:
        try:
            await check_for_new_projects()
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
        await asyncio.sleep(60) 



from flask import Flask, jsonify
from threading import Thread
from multiprocessing import Process, Queue
# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "Hello, world!"})

@app.route('/keywords')
def get_keywords():
    return jsonify({
        "keywords": "",
        "block_keywords": "normalized_block_keyword_list"
    })

# Function to run Flask app
def run_flask():
    app.run(host='0.0.0.0', port=7860)


# Function to run both Flask and asyncio main
def run_all():


    # Start the Flask thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Run the main asyncio loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_loop())

    # Clean up

    flask_thread.join()

if __name__ == "__main__":
    nest_asyncio.apply()
    logging.basicConfig(level=logging.INFO)
    run_all()