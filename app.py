
import requests
import asyncio
import nest_asyncio
from bs4 import BeautifulSoup
from telegram.helpers import escape_markdown
from telegram import Bot
import logging
from flask import Flask, jsonify
from threading import Thread

import os
from deep_translator import GoogleTranslator
from together import Together
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler, filters, Updater
import logging
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram Bot Token
TOKEN = '7893336962:AAE-CWOXuwE9nlU5pJZRNoTMJBusWBPyuVk'
CHAT_ID = '6246129018'
api_key = "bcd2a5d64013cef1085dcfe213b42f470c55eb7025bb4d06033ce8fd5463dcf5"

class AITranslatorClient:
    def __init__(self, api_key):
        self.client = Together(api_key=api_key)
        self.translator = GoogleTranslator()

    def translate_to_english(self, message):
        my_translator = GoogleTranslator(source='auto', target='en')
        result = my_translator.translate(text=message)

        print(result)
        return result, my_translator.source

    def translate_to_original(self, message, src_lang):
        """Translate the message back to the original language."""
        my_translator = GoogleTranslator(source='auto', target='ar')
        result = my_translator.translate(text=message)

        print(result)
        return result

    def create_prompt(self, client_message):
        """Generate the full AI prompt with the client's message."""
        template_prompt = (
            "As a freelancer with expertise in attracting clients, generate a strong and eloquent response "
            "to the following client’s message. The response should be concise, persuasive, and appear human-written, "
            "not by artificial intelligence. Ensure it highlights my skills, experience, or services that align with "
            "the client’s needs, without including any expressions of welcome, thank you, or farewell. "
            "Keep in mind that the client has not yet chosen me to work with them, and the goal of the message is to "
            "encourage them to do so. Here’s the client’s message:' [insert client’s message here] '."
            "\n\nPlease ensure the response follows these key points:\n"
            "1. Acknowledge the client’s needs and demonstrate clear understanding.\n"
            "2. Highlight specific skills or services that make me the ideal choice.\n"
            "3. Persuade the client with a confident tone, but keep the response short and focused.\n"
            "4. Include a call to action to engage the client in further discussion or suggest the next steps."
        )
        return template_prompt.replace("[insert client’s message here]", client_message)

    def get_ai_response(self, prompt):
        print(prompt)
        """Make a request to the AI and get a response."""
        response = self.client.chat.completions.create(
            model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=61651,
    temperature=0.7,
    top_p=0.7,
    top_k=50,
    repetition_penalty=1,
    stop=["<|eot_id|>","<|eom_id|>"],
            stream=False

        )
        print(response)
        return response.choices[0].message.content

    def get_prompt_english(self, user_message):
        translated_message, original_lang = self.translate_to_english(user_message)
        prompt = self.create_prompt(translated_message)
        return prompt
    
    def process_message(self, user_message):
        """Main process to translate message, send to AI, and translate response back."""
        # Step 1: Translate user's message to English
        translated_message, original_lang = self.translate_to_english(user_message)

        # Step 2: Create prompt with translated message
        prompt = self.create_prompt(translated_message)

        # Step 3: Get AI's response based on the prompt
        ai_response_in_english = self.get_ai_response(prompt)

        # Step 4: Translate AI's response back to the original language
        ai_response_in_original = self.translate_to_original(ai_response_in_english, original_lang)

        return ai_response_in_original

class MostaqlScraper:
    def __init__(self):
        self.url = 'https://mostaql.com/projects?category=development&budget_max=10000&sort=latest'
        self.headers = {
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
            # Add your own cookie values
            'Cookie': 'XSRF-TOKEN=your_token; mostaqlweb=your_value'
        }
        self.previous_projects = set()

    def scrape_projects(self):
        """Scrape the Mostaql website for projects."""
        try:
            response = requests.get(self.url, headers=self.headers)
            if response.status_code == 200:
                return self.parse_projects(response.text)
            else:
                logger.error(f"Failed to fetch projects. Status code: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error scraping projects: {e}")
            return []

    def parse_projects(self, html):
        """Parse the scraped HTML content."""
        soup = BeautifulSoup(html, 'html.parser')
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


    def get_project_description(self, url):
        """Fetch and parse the project description from the given URL."""
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                description_div = soup.find('div', id='project-brief')
                if description_div:
                    description = description_div.find('div', class_='carda__content')
                    if description:
                        return description.get_text(strip=True)
                    else:
                        return "Description not found."
                else:
                    return "Project brief section not found."
            else:
                logger.error(f"Failed to fetch project description. Status code: {response.status_code}")
                return "Failed to fetch project description."
        except Exception as e:
            logger.error(f"Error fetching project description: {e}")
            return f"Error fetching project description: {str(e)}"

class ProjectChecker:
    def __init__(self, scraper, notifier):
        self.scraper = scraper
        self.notifier = notifier

    async def check_for_new_projects(self):
        """Check for new projects and notify if any are found."""
        projects = self.scraper.scrape_projects()
        new_projects = [(title, url, time, offers) for title, url, time, offers in projects if url not in self.scraper.previous_projects]

        for title, url, time, offers in new_projects:
            message = (f"New Project: {title}\n"
                       f"Time: {time}\n"
                       f"Link: {url}")
            await self.notifier.send_notification(message)

        # Update the set of seen projects
        self.scraper.previous_projects.update([url for _, url, _, _ in projects])


class AsyncRunner:
    def __init__(self, project_checker, interval=60):
        self.project_checker = project_checker
        self.interval = interval

    async def main_loop(self):
        """Run the main loop for checking new projects."""
        while True:
            try:
                await self.project_checker.check_for_new_projects()
            except Exception as e:
                logger.error(f"An error occurred: {e}")
            await asyncio.sleep(self.interval)


class WebServer:
    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route('/')
        def index():
            return jsonify({"message": "Hello, world!"})

        @self.app.route('/keywords')
        def get_keywords():
            return jsonify({
                "keywords": "",
                "block_keywords": "normalized_block_keyword_list"
            })

    def run(self):
        """Run the Flask app."""
        self.app.run(host='0.0.0.0', port=7860)

class Application:
    def __init__(self, chat_id, scraper, interval=60):
        self.chat_id = chat_id
        self.client = AITranslatorClient(api_key)
        self.scraper = scraper
        self.web_server = WebServer()
        self.telegram_app = ApplicationBuilder().token(TOKEN).build()
        self.async_runner = AsyncRunner(ProjectChecker(scraper, self), interval)

    def setup_telegram_handlers(self):
        """Set up handlers for Telegram bot commands and callback queries."""
        self.telegram_app.add_handler(CommandHandler("start", self.start_command))
        self.telegram_app.add_handler(CallbackQueryHandler(self.handle_button_click))

    async def start_command(self, update: Update, context):
        """Handle the /start command."""
        await update.message.reply_text("Bot started. You will receive project notifications.")

    async def run_telegram_bot(self):
        """Run the Telegram bot."""
        await self.telegram_app.initialize()
        await self.telegram_app.start()
        await self.telegram_app.updater.start_polling()

    async def send_notification(self, message):
        """Send a notification via Telegram with inline keyboard buttons."""
        try:
            keyboard = [
                [InlineKeyboardButton("Get AI Prompt", callback_data='get_prompt')],
                [InlineKeyboardButton("Get Final AI Response", callback_data='get_response')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await self.telegram_app.bot.send_message(
                chat_id=self.chat_id, 
                text=message,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def handle_button_click(self, update: Update, context):
        """Handle button clicks for AI prompt and final response."""
        query = update.callback_query
        await query.answer()

        original_message = query.message.text
        chat_id = query.message.chat_id
        message_id = query.message.message_id  # Get the original message ID
        url = original_message.split('\n')[-1].replace('Link: ', '')

        # Fetch the project description
        description = self.scraper.get_project_description(url)

        if query.data == 'get_prompt':
            prompt = self.client.get_prompt_english(description)
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"{prompt}",
                reply_to_message_id=message_id  # Reply to the original message
            )

        elif query.data == 'get_response':
            final_response = self.client.process_message(description)
            await context.bot.send_message(
                chat_id=chat_id, 
                text=f"{final_response}",
                reply_to_message_id=message_id  # Reply to the original message
            )


    async def run(self):
        """Run the Flask server, async project checker, and Telegram bot."""
        self.setup_telegram_handlers()
        flask_thread = Thread(target=self.web_server.run)
        flask_thread.start()
        await asyncio.gather(
            self.run_telegram_bot(),
            self.async_runner.main_loop()
        )
        flask_thread.join()

if __name__ == "__main__":
    import asyncio
    import nest_asyncio
    
    nest_asyncio.apply()

    scraper = MostaqlScraper()
    app = Application(CHAT_ID, scraper)

    asyncio.run(app.run())
