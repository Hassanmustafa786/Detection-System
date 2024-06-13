# Fraud Detection System Using Audio Conversations

This project is a fraud detection system that takes audio as input (a conversation between an agent and a customer), converts it into text using Whisper, processes the text, and detects if the agent is committing fraud. The project is built using Flask and incorporates several libraries to handle audio processing, language detection, and translation.

## Features

- Converts audio conversations to text using Whisper.
- Detects fraud in agent-customer conversations.
- Utilizes various libraries for language processing and translation.
- Built using Flask framework.

## Libraries and Tools Used

- `re` - Regular expression operations
- `os` - Miscellaneous operating system interfaces
- `io` - Core tools for working with streams
- `time` - Time access and conversions
- `uuid` - Universally unique identifiers
- `gtts` - Google Text-to-Speech
- `speech_recognition` - Speech recognition library
- `dotenv` - Load environment variables from a `.env` file
- `langchain_openai` - OpenAI integration for LangChain
- `deep_translator` - Simple and powerful translation library
- `operator` - Standard operator functions
- `langchain.memory` - Memory components for LangChain
- `langchain.prompts` - Prompt templates for LangChain
- `langchain_core.runnables` - Runnable components for LangChain
- `openai` - OpenAI API client
- `langdetect` - Language detection library

## Project Structure

- `merge.py` - The main Flask application file
- `templates/` - Directory containing HTML templates
- `static/` - Directory containing static files (CSS, JS, images)
- `.env` - Environment variables file
- `requirements.txt` - Python dependencies

## Prerequisites

Before running the application, ensure you have the following installed:

- Python 3.10.0
- Necessary libraries listed in `requirements.txt`

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Hassanmustafa786/Detection-System
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required libraries:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file and add your environment variables:

    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

## Running the Application

To start the Flask application:

1. Ensure your virtual environment is activated.
2. Run the Flask app:

    ```bash
    python merge.py
    ```

3. Open your browser and navigate to `http://127.0.0.1:5000`.


## Usage

1. Upload an audio file of a conversation between an agent and a customer.
2. The system will convert the audio to text using Whisper.
3. The text will be processed to detect if the agent is committing fraud.
4. The results will be displayed on the web interface.

## Contact

If you have any questions or need further assistance, feel free to reach out to me at hassanqureshi700@gmail.com.

---

**Hafiz Hassan Mustafa**
