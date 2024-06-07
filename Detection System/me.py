import streamlit as st
from openai import OpenAI

def transcribe(file_path):
    # Initialize the OpenAI client
    client = OpenAI()

    # Create transcription
    transcription = client.audio.transcriptions.create(
        model="whisper-1", 
        file=file_path
    )
    # Return the transcription text
    return transcription.text

# Streamlit app
def main():
    st.title('Whisper')
    code = '''Made by Hassan Mustafa.'''
    st.code(code, language='python')

    uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "flac"])

    if uploaded_file:
        if st.button('Transcribe'):
            transcription = transcribe(uploaded_file)
            st.subheader('Transcription:')
            st.text_area("Transcription Output", value=transcription, height=200)

if __name__ == '__main__':
    main()