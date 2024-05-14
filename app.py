from urllib import request
from youtube_transcript_api import YouTubeTranscriptApi
from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv
import os
import nltk
from bs4 import BeautifulSoup
import requests  
from deepmultilingualpunctuation import PunctuationModel
import time
import scrapetube



# Load environment variables from .env file
load_dotenv()
#Check if the punkt tokenizer is already downloaded
if not nltk.data.find('tokenizers/punkt'):
    nltk.download('punkt')
# Access variables securely
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4-turbo')  # Provide a default value if not set
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.openai.com/v1')  # Provide a default value if not set
MAX_RETRIES  = 5


async def generate_response(user_prompt, model, api_key, base_url="https://api.openai.com/v1", temperature=0.7):
    response = None
    async_openai_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )   

    for attempt in range(MAX_RETRIES):
        try:
            completion = await async_openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional transcript editor. You transform unformatted transcripts with bad or no punctuation, no formatting or just raw text, into perfectly formatted documents. You reformat text by removing and umms and ahmms, repeated words or rephrased words. Incorrectly placed punctuation, such as commas, semicolons, or periods, are removed. Uncessarily short sentences are merged. Return just the reformatted text, no labels, no titles, no headings, not a summary but only the full text. Keep the text and words as close to the original as possible without being gramartically incorrect. and avoid using synonymns or replacing words with similar words. Don't leave any notes,never ever say here is the reformatted text! no notes are required, infact, I hate notes! Just return any provided transcript perfectly formatted and ready to read."},
                    {"role": "user", "content": "Here is the user prompt for formatting: " + user_prompt}],
                temperature=temperature,
            )
            response = completion.choices[0].message.content

        except Exception as e:
            if attempt < MAX_RETRIES - 1:  # don't wait after the last attempt
                await asyncio.sleep(1 * (2**attempt))
            else:
                print(f"Response generation exception after max retries: {e}")
                return None
        return response
    
async def generate_transcript(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    full_transcript = ""
    for t in transcript:
        full_transcript += t['text'] + " "
    return full_transcript

def punctuate_text(text):
    model = PunctuationModel()
    result = model.restore_punctuation(text)
    return result



def find_sentence_boundaries(text):
    sentences = nltk.sent_tokenize(text)
    return sentences

def count_words(transcript):
    words = transcript.split()
    return len(words)

async def main():
    #start timer
    start_time = time.time()
    #get all videos from channel
    videos = scrapetube.get_channel("UCbaQv8_DS1n8puOnJRzLPzw")
    for vid in videos:
        #start vid_timer
        vid_start_time = time.time()
        transcript = await generate_transcript(vid)
        print("TRANSCRIPT RETRIEVED")
        transcript = punctuate_text(transcript)
        print("TRANSCRIPT PUNCTUATED")
        sentences = find_sentence_boundaries(transcript)
        print("SENTENCES FOUND")
        #create 10 sentence chunks
        chunks = []
        for i in range(0, len(sentences), 10):
            chunks.append(' '.join(sentences[i:i+10]))
        print("CHUNKS")
        # #get the youtube video title
        url = f"https://www.youtube.com/watch?v={vid}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title').text
        title = title.split(' - ')[0]

        for chunk in chunks:
            print("CHUNK")
            response = await generate_response(chunk, LLM_MODEL, API_KEY, BASE_URL, 0)
            # Write the response to a file named after the video ID in the transcripts folder
            with open(f"transcripts/{title}", "a") as file:
                if file.tell() == 0:  # Check if file is empty to write metadata at the top
                    file.write(f"#DANSWER_METADATA={{{{'link': 'https://www.youtube.com/watch?v={vid}'}}}}\n")
                file.write(response + "\n")
                # indicate progress based on the number of chunks
                print(f"Progress: {chunks.index(chunk) + 1}/{len(chunks)}")
            print("CHUNK WRITE")
        print(f"Wrote transcript to file: {title}")
        video_duration_seconds = time.time() - vid_start_time
        video_minutes = int(video_duration_seconds // 60)
        video_seconds = int(video_duration_seconds % 60)
        print(f"Time taken for video {title}: {video_minutes} minutes and {video_seconds} seconds")
        
    total_duration_seconds = time.time() - start_time
    total_minutes = int(total_duration_seconds // 60)
    total_seconds = int(total_duration_seconds % 60)
    print(f"Time taken for all videos: {total_minutes} minutes and {total_seconds} seconds")

if __name__ == "__main__":
    asyncio.run(main())
