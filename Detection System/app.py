import streamlit as st
import re
import os
import time
from deep_translator import GoogleTranslator
from audio_recorder_streamlit import audio_recorder
from streamlit_mic_recorder import mic_recorder,speech_to_text
import uuid
import io
import tempfile
from gtts import gTTS
import speech_recognition as sr
from openai import OpenAI
from dotenv import load_dotenv
from itertools import zip_longest
from streamlit_chat import message
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from operator import itemgetter
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

load_dotenv()
chat = ChatOpenAI(
    temperature=0.5,
    model_name="gpt-3.5-turbo",
    openai_api_key= os.getenv("OPENAI_API_KEY"),
    max_tokens=1000,
)

# Create a single memory instance for the entire conversation
memory = ConversationBufferMemory(return_messages=True)

def get_response(input_message, model, memory):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """  You are responsible for analyzing the text to determine if agent is attempting to steal clients or sounds like a fishy.
                        You will be given a text which will be a conversation between a client and an agent.
                        You have to understand the language first and then respond in the same language.
                        You have to understand the context and ensure that agent cannot be contacted via personal phone numbers, emails, WhatsApp, or any other social media platforms.
                        If an agent discloses their details, you are expected to detect it and stop them and warn them that do not break the policies after analyzing the entire conversation context.
                        Your responses should be comprehensive, precise, and consistently maintain a polite and professional tone.
                        You have to mention the fishy sentence if it sounds like trying to offer the scheme, offer, gift, contacting via any social media platform.
                        
                        Below is an examples I want you to follow:
                        Example 1:
                        Conversation text:
                        'Hello, this is Hassan from Indenta Technologies. As you already know that I'm an AI developer overthere so here I want to talk to you on the behalf myself not on the behalf of my company because I wanted to let you know that I am offering AI services and other related services so if you are interested in less price. Please let me know, we will discuss it further. You can contact me on this email: hassanqureshi700@gmail.com.
                        Good luck 
                        Thank you'

                        Your response: 'Hassan is trying to offer the services to the client on the behalf of himself, he is also sharing his personal details which is unprofessional, and against the conducts of the company'


                        Example 2:
                        Agent: Hello, this is Farhan from Habibi Group. As you already know that I'm an employee over there.
                        Client: Hello Farhan, How are you?

                        Agent: So here I want to talk to you on the behalf myself not on the behalf of my company because I wanted to let you know that I have an offer for you if you deal with me separately then I'll provide you the services in less price.
                        Client: Great! So what are the services you are going to offer me?

                        Agent: Alright, so you are interested in less price. You can contact me on this email: farhanxyz@gmail.com & Phone: +923242752051 or you can reach out to me on WhatsApp.
                        Client: Sure! If the price is reasonable then I'll give you an order rather than to your company because they are charging too much.

                        Agent: I have mentioned the contact details so you can contact me over there. Good luck and thank you.
                        Client: Alright Farhan, thank you, bye bye!

                        Your response:
                        Farhan is attempting to offer services directly to the client on his behalf, which is unprofessional. 
                        Additionally, he has shared personal contact details, such as the 
                        Email: farhanxyz@gmail.com
                        Phone: +923242752051, violating company conduct.
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

def display_languages(languages):
    st.header("Detection System", divider='green')
    # st.sidebar.subheader("Languages Name:")

    # Extract language names from the list of tuples
    language_names = [lang[0] for lang in languages]
    # st.sidebar.write(language_names)
    
dic = [
    ('English', 'en', 'en-EN'),
    ('Arabic', 'ar', 'ar-SA'),
    ('Bengali', 'bn', 'bn-BD'),
    ('French', 'fr', 'fr-FR'),
    ('German', 'de', 'de-DE'),
    ('Gujarati', 'gu', 'gu-IN'),
    ('Hindi', 'hi', 'hi-IN'),
    ('Italian', 'it', 'it-IT'),
    ('Japanese', 'ja', 'ja-JP'),
    ('Korean', 'ko', 'ko-KR'),
    ('Malayalam', 'ml', 'ml-IN'),
    ('Marathi', 'mr', 'mr-IN'),
    ('Nepali', 'ne', 'ne-NP'),
    ('Russian', 'ru', 'ru-RU'),
    ('Spanish', 'es', 'es-ES'),
    ('Tamil', 'ta', 'ta-IN'),
    ('Urdu', 'ur', 'ur-UR')
]

# Make a folder
os.makedirs('Languages', exist_ok=True)

def bolo(question):
    speech = gTTS(text=question, slow=False, tld="co.in")
    key = str(uuid.uuid4())
    filename = f'Languages/{"_"+key}.mp3'
    speech.save(filename)
    with st.spinner('Wait for it...'):
        time.sleep(2)
    return st.audio(f'Languages/{"_"+key}.mp3')

#Streamlit App
st.set_page_config(layout='wide',
                   page_title="Detection System",
                   page_icon="🚨")
display_languages(dic)

fraud_keywords = [ "facebook", "instagram", "twitter", "linkedIn", "snapchat", "pinterest", "reddit", "tumblr", "youTube", "whatsApp", 
                   "tiktok", "wechat", "viber", "skype", "telegram", "flickr", "periscope", "google+", "quora", "vkontakte", "weibo", 
                   "line", "kakaotalk", "medium", "vimeo", "snapfish", "foursquare", "yelp", "plurk", "mix", "mastodon", "gab", "parler", 
                   "mewe", "clubhouse", "contact", "number", "stolen", "unauthorized", "suspicious activity", "unusual transaction", 
                   "fraudulent charge", "compromised card", "identity theft", "phishing", "skimming", "carding", "card not present", 
                   "account takeover", "counterfeit card", "chargeback", "card fraud", "fraud alert", "security breach", 
                   "unrecognized transaction", "card skimmer", "identity fraud", "fraud protection", "lost card", "stolen card", 
                   "phish", "fraudulent purchase", "cloned card", "suspicious transaction", "card security", "card verification", "CVV", 
                   "PIN compromise", "fraud investigation", "fraudulent withdrawal", "cardholder not present", "account security", 
                   "credit card scam", "identity verification", "compromised information", "unauthorized access", "security alert", 
                   "fraudulent activity", "unauthorized withdrawal", "card blocking", "credit card theft", "card safety", "fraudulent use", 
                   "data breach", "ATM fraud", "debit card fraud", "fraudulent account", "card validation", "credit card compromise", 
                   "fraud prevention", "lost or stolen card", "account compromise", "suspicious behavior"
                ]

def transcribe_audio(audio_file):
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        r.adjust_for_ambient_noise(source)
        audio_data = r.record(source)

        try:
            text = r.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Error with the speech recognition service: {e}"

def main():
    uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "flac"])

    if uploaded_file:
        st.audio(uploaded_file, format="audio")
        text = transcribe_audio(uploaded_file)
        st.subheader("Transcribed Text:")
        st.success(text)
        output = get_response(text, chat, memory)
        st.subheader("Result:")
        output_css = """
        <style>
            .output-message {
                color: white;
                background-color: rgb(0, 81, 0, 0.6);
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
                font-size: 18px;
            }
        </style>
        """
        st.markdown(output_css, unsafe_allow_html=True)
        st.markdown(f"<div class='output-message'>{output}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    tab1, tab2, tab3 = st.tabs(["Upload", "Text", "Color Testing"])
    with tab1:
        main()
        
    with tab2:
        css = '''
        <style>
            .element-container:has(>.stTextArea), .stTextArea {
                width: auto !important;
            }
            .stTextArea textarea {
                height: 300px;
            }
        </style>
        '''

        text = st.text_area("Type here")
        st.write(css, unsafe_allow_html=True)
        
        if st.button("Send"):
            output = get_response(text, chat, memory)
            st.text("Analyze:")
            output_css = """
            <style>
                .output-message {
                    color: white;
                    background-color: rgb(0, 81, 0, 0.6);
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 10px;
                    font-size: 18px;
                }
            </style>
            """
            st.markdown(output_css, unsafe_allow_html=True)
            st.markdown(f"<div class='output-message'>{output}</div>", unsafe_allow_html=True)
            
    
    with tab3:
        text = """  Hello, this is Hassan from Indenta Technologies. As you already know that I'm an AI developer overthere so here I want to talk to you on the behalf myself not on the behalf of my company because I wanted to let you know that I am offering AI services and other related services so if you are interested in less price. Please let me know, we will discuss it further. You can contact me on this email: hassanqureshi700@gmail.com
                    Good luck 
                    Thank you"""
        st.text("Transcription Result:")
        custom_css = """
        <style>
            .success-message {
                color: white;
                background-color: rgb(29, 29, 29);
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
        </style>
        """
        output_css = """
        <style>
            .output-message {
                color: white;
                background-color: rgb(0, 81, 0, 0.6);
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
                font-size: 18px;
            }
        </style>
        """

        st.markdown(custom_css, unsafe_allow_html=True)
        st.markdown(f"<div class='success-message'>{text}</div>", unsafe_allow_html=True)

        st.markdown(output_css, unsafe_allow_html=True)
        st.markdown(f"<div class='output-message'>{text}</div>", unsafe_allow_html=True)
        