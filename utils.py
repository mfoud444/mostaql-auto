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
            "to the following client’s message. The response should be concise, persuasive, and appear human-written, "
            "not by artificial intelligence. Ensure it highlights my skills, experience, or services that align with "
            "the client’s needs, without including any expressions of welcome, thank you, or farewell. "
            "Keep in mind that the client has not yet chosen me to work with them, and the goal of the message is to "
            "encourage them to do so. Here’s the client’s message: [insert client’s message here]."
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


# Main script logic
if __name__ == "__main__":
    # Initialize the API client with Together API key
    api_key = "bcd2a5d64013cef1085dcfe213b42f470c55eb7025bb4d06033ce8fd5463dcf5"#os.environ.get('TOGETHER_API_KEY')
    client = AITranslatorClient(api_key)

    # Ask the user for the client message
    user_message = "عندي موقع كان راكب عليه بلقنات كثير وثيمات ولغيتها بعضهم كان نسخة nulled وبعضهم اصلي وارغب الآن في حذف جداول البيانات القديمة المتعلقة هذه الثيمات والاضافات القديمة لتحسين أداء قاعدة البيانات وكمان ارغب في فحص وازالة الأكواد الخبيثة من الموقع بالكامل اذا كانت موجوده فيه وعمل صيانة شاملة للموقع"#input("Please enter the client's message: ")

    # Process the message through translation and AI response generation
    final_response = client.process_message(user_message)

    # Print the final response in the original language
    print("\nAI Response:\n", final_response)