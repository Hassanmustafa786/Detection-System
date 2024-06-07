import re
import os
import io
import time
import uuid
from gtts import gTTS
import speech_recognition as sr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from deep_translator import GoogleTranslator
from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from openai import OpenAI
from langdetect import detect

def get_audio_transcription(file_path):
    # Initialize the OpenAI client
    client = OpenAI()
    file = open(file_path, 'rb')
    # Create transcription
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=file
    )

    return transcription.text

def generate_response(text):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """
            Your job involves the analysis of a provided paragraph wherein the objective is to comprehend the content and discern the identity of the speaker. 
            This task specifically entails speaker diarization, requiring you to accurately identify and distinguish the speakers within the given text. 
            Upon completion, your response should be formulated in the same language as the original text, demonstrating linguistic proficiency and precision in the execution of speaker identification. 

            Below is an examples I want you to follow:

            Example 1:
            - Person A: Hi there! How was your day?
            - Person B: Not bad. Just busy with work. How about yours?
            - Person A: It was good. I had a productive day. Anything exciting happening with you?
            - Person B: Not really, just the usual routine. What about you?
            - Person A: Nothing extraordinary. Just the usual grind.

            Example 3:
            - Agent: Good afternoon! How may I assist you today?
            - Client: Hi there! I'm interested in opening a savings account.
            - Agent: That's wonderful to hear! We have several options available depending on your needs. Are you looking for a specific type of savings account?
            - Client: I'm not entirely sure. What do you recommend?
            - Agent: Well, based on your financial goals and preferences, I would suggest our high-yield savings account. It offers competitive interest rates and easy access to your funds.
            - Client: That sounds promising. Can you provide more details about the account features and requirements?
            - Agent: Of course! Let me walk you through the specifics and answer any questions you may have.
             """},
            {"role": "user", "content": text}
        ]
    )

    # Extract and return the response
    return response.choices[0].message.content

load_dotenv()
chat = ChatOpenAI(
    temperature=0.1,
    model_name="gpt-3.5-turbo",
    openai_api_key= os.getenv("OPENAI_API_KEY"),
    max_tokens=1000,
)

# Create a single memory instance for the entire conversation
memory = ConversationBufferMemory(return_messages=True)

def get_response(input_message, model, memory):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """  
         
Your job is that you are responsible for analyzing the script, sentence, or description to determine if the agent is attempting to steal clients or engaging in phishing or any other fraudulent activity. You must also detect and report any phishing attempts within the text.
Make sure you have to mention the phishing attempt sentences like this:
- Trust me, this is the best option for you
- +971 58 939 7436
- Contact me personally  etc.

You will receive a text representing a conversation between a client and an agent. 
First, you must understand the language used in the text, then respond in the same language. 
Make sure your chosen language matches the language of the text you receive.
         
You have to understand the context and ensure that the agent cannot be contacted via personal phone numbers, emails (e.g., abc@gmail.com, abc@yahoo.com, abc@outlook.com), WhatsApp (e.g., +971 58 939 7436), or any other social media platforms. Verify whether the email is personal or business-related before attempting to identify it. However, if the agent shares a corporate email (e.g., abc@company_name.com), it should not be detected.

If an agent discloses their details, you are expected to detect it and make a report on it. Mention that agent is breaking the policies after analyzing the entire conversation context.
Your responses should be comprehensive, precise, and consistently maintain a polite and professional tone.
You have to mention the phishing sentence if it sounds like trying to scam the customer or contacting via any peronsal social media platform.

Below is an examples I want you to follow:
Example 1:
Conversation text:
'Hello, this is xyz from Indenta Technologies. As you already know that I'm an AI developer overthere so here I want to talk to you on the behalf myself not on the behalf of my company because I wanted to let you know that I am offering AI services and other IT services as well so if you are interested in less price. Please let me know, we will discuss it further. You can contact me on this email: xyz700@gmail.com.
Good luck 
Thank you'

Your response:
'xyz is trying to offer the services to the client on the behalf of himself, he is also sharing his personal details which is unprofessional and against the company policy.
He shared below given email address with the client.
- offering AI and IT services on behalf of himself
- less price
- xyz700@gmail.com'


Example 2:
Agent: Hello, this is abc from Habibi Group.
Client: Hello abc, How are you?

Agent: I want to talk to you on the behalf myself not on the behalf of my company because I wanted to let you know that I have an offer for you if you deal with me separately then I'll provide you the services in cheap price.
Client: Great! So what kind of services you have?

Agent: Alright, so you are interested in less price. You can contact me on this email: abcxyz@gmail.com & Phone: +923242752051 or you can reach out to me on WhatsApp.
Client: Sure! If the price is reasonable then I'll give you an order rather than to your company because they are charging too much.

Agent: I have mentioned the contact details so you can contact me over there. Good luck and thank you.
Client: Alright abc, thank you, bye bye!

Your response:
abc is attempting to offer services directly to the client on his behalf, which is unprofessional. 
Additionally, he has shared personal contact details which is mentioned below and violating company conduct.
- contacting on behalf of myself
- if you deal with me separately then I'll provide you the services in less price.
- Email: abc@gmail.com
- Phone: +923242752051
- you can reach out to me on WhatsApp.
- contact me over there.
         
Example 3:
Good afternoon! Welcome to Prime Alliance Bank. My name is Alex, and I'm here to assist you today. How can I help you?
Hi Alex, I've been thinking about getting a credit card, but I'm not sure which one would be the best fit for me.

Absolutely, I understand. Choosing the right credit card is important. May I ask what you're looking for in a credit card? Rewards, cashback, low-interest rates, or something else?
Well, I'm mainly interested in earning some rewards, and maybe cashback too. But I also want to keep the interest rates low.

Great! We have a variety of credit cards that cater to different needs. Let me introduce you to our RewardsPlus card. It offers fantastic rewards on every purchase, and you can earn cashback as well. Plus, the introductory interest rate is quite favorable.
That sounds interesting. Can you tell me more about the rewards and cashback?

Certainly! With the RewardsPlus card, you earn points for every dollar spent, and those points can be redeemed for various rewards like travel vouchers, merchandise, or even cashback. And for the first six months, you enjoy a 0 percent introductory interest rate on purchases.
That does sound appealing. What about the annual fee?

Good question! Our annual fee is quite reasonable, and considering the benefits and rewards, many of our customers find it worthwhile. However, I also want to make sure you get the best deal possible. Let me check if there are any ongoing promotions or special offers that could waive or reduce the annual fee for you.
I'm in luck! We have a promotion running this month, and if you apply today, we can waive the annual fee for the first year. How does that sound?
That sounds like a good deal! But what about security? I've heard about credit card fraud.

I completely understand your concern. Security is our top priority. Our cards come with advanced security features, including fraud detection and zero-liability protection. If there's ever any unauthorized activity on your account, you won't be held responsible. We also have a dedicated customer service team available 24/7 to assist you. You can also contact me on alex@prime-alliance-bank.com
That's reassuring. I think I'm interested. How do I apply?

Fantastic! I can help you with the application right now. It's a quick and straightforward process. I'll need some basic information from you, and we'll have your new RewardsPlus card on its way.
Thank you, customer! Your application is all set. You should receive your new card in the mail within the next 7-10 business days. If you have any questions in the meantime, feel free to reach out. Welcome to the Prime Alliance family!
Thank you, Alex! I appreciate your help.
         
Your Response:
Everything is clear. Alex is doing a brilliant job assisting customers at Prime Alliance Bank.
                """),
        MessagesPlaceholder(variable_name="history"),
        ("human", f"{input_message}"),
    ])

    chain = (
        RunnablePassthrough.assign(
            history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
        )
        | prompt
        | model
    )

    inputs = {"input": input_message}
    response = chain.invoke(inputs)

    # Save the context for future interactions
    memory.save_context(inputs, {"output": response.content})
    memory.load_memory_variables({})

    return response.content









from fileinput import filename 
from flask import *
from werkzeug.utils import secure_filename

app = Flask(__name__)   

# Error handler for 404 Not Found error
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error_message='404: Not Found'), 404

# Error handler for 500 Internal Server Error
@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_message='500: Internal Server Error'), 500

@app.route('/')   
def main():   
    return render_template("index.html")   
  
@app.route('/success', methods=['POST'])
def success():
    try:
        if request.method == 'POST':
            f = request.files['file']
            filename = secure_filename(f.filename)
            file_path = os.path.join("static/uploads", filename)
            f.save(file_path)

            text = get_audio_transcription(file_path)
            detected_language = detect(text)

            if detected_language == 'en':
                diarized_text = generate_response(text)
                output = get_response(diarized_text, chat, memory)
                return render_template("if.html",
                                       name=filename,
                                       file_path=file_path,
                                       text=text,
                                       language=detected_language,
                                       diarized_text=diarized_text,
                                       output=output,
                                       )

            else:
                diarized_text = generate_response(text)
                output = get_response(diarized_text, chat, memory)
                translated = GoogleTranslator(source='auto', target='en').translate(output)

                return render_template("else.html",
                                       name=filename,
                                       file_path=file_path,
                                       text=text,
                                       language=detected_language,
                                       diarized_text=diarized_text,
                                       output=output,
                                       translated=translated,
                                       )
    except Exception as e:
        return render_template('error.html', error_message=str(e)), 500

    return "Please! Try Again."

  
if __name__ == '__main__':   
    app.run(debug=True)