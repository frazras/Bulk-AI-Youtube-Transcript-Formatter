# Bulk-AI-Youtube-Transcript-Formatter
This repository contains two Python scripts designed to fetch and format YouTube video transcripts. The first script, `app.py`, provides basic functionality for fetching transcripts, while the second script, `app_advanced.py`, includes additional features such as punctuation restoration and formatting using AI models

# Prerequisites
Before running the scripts, ensure you have Python installed on your system. Python can be downloaded from python.org. You will need Python 3.6 or higher.

# Common Setup Steps
1. Clone the Repository:
Open a terminal (Command Prompt on Windows, Terminal app on macOS and Linux) and run the following command:

````
   git clone https://github.com/yourusername/Bulk-AI-Youtube-Transcript-Formatter.git
   cd Bulk-AI-Youtube-Transcript-Formatter
````

2. Install Required Libraries:
Both scripts have external dependencies which can be installed via pip. Run:
````
   pip install -r requirements.txt
````

3. Environment Variables:
For app_advanced.py, you need to set up environment variables. Create a .env file in the project root directory and add the following:
````
   LLM_MODEL="gpt-3.5-turbo-1106"
   API_KEY="your_openai_api_key"
   BASE_URL="https://api.openai.com/v1"
````

Replace "your_openai_api_key" with your actual OpenAI API key.

# Running app.py
## Description
app.py fetches YouTube video transcripts for a specified channel and saves them to a local directory.
## Steps to Run
1. Open your terminal and navigate to the project directory.
2. Run the Script:
   ``   python app.py``

Follow the on-screen prompts to enter the YouTube channel username and select the content type (Videos, Streams, or Both).

## Running app_advanced.py
### Description
`app_advanced.py` enhances the basic functionality by adding punctuation, formatting the transcript using an AI model, and saving the formatted transcript.
### Additional Setup
#### NLTK Data:
The script uses NLTK for sentence tokenization. You might need to download the NLTK data manually if it's not already present:
````
  import nltk
  nltk.download('punkt')
````

Steps to Run
1. Open your terminal and navigate to the project directory.
2. Run the Script:

````
   python app_advanced.py
````

Similar to `app.py`, follow the on-screen prompts.
Notes
Ensure you have a stable internet connection as the scripts interact with online APIs.
The scripts are designed to handle basic errors such as disabled transcripts; however, always check the console for error messages.
By following these instructions, you should be able to run both scripts successfully on Windows, macOS, and Linux.