i want added 2 keyboard button (1 - get prompt for ai, 2- get final response ai) for every message telegram


import os
from googletrans import Translator
from together import Together

# Define the class for handling translation and AI interaction
class AITranslatorClient:
    def __init__(self, api_key):
        self.client = Together(api_key=api_key)
        self.translator = Translator()

    def translate_to_english(self, message):
        """Translate the message to English."""
        translation = self.translator.translate(message, dest='en')
        print(translation.text)
        return translation.text, translation.src

    def translate_to_original(self, message, src_lang):
        """Translate the message back to the original language."""
        translation = self.translator.translate(message, dest=src_lang)
        return translation.text

    def create_prompt(self, client_message):
        """Generate the full AI prompt with the client's message."""
        template_prompt = (
            "As a freelancer with expertise in attracting clients, generate a strong and eloquent response "
  
            "encourage them to do so. Here’s the client’s message: [insert client’s message here]."
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


# Main script logic
if __name__ == "__main__":
    # Initialize the API client with Together API key
    api_key = "bcd2a5d64013cef1085dcfe213b42f470c55eb7025bb4d06033ce8fd5463dcf5"#os.environ.get('TOGETHER_API_KEY')
    client = AITranslatorClient(api_key)

    # Ask the user for the client message
    user_message = """

    final_response = client.process_message(user_message)

    # Print the final response in the original language
    print("\nAI Response:\n", final_response)