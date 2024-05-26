from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from openai import AsyncOpenAI
import asyncio
from dotenv import load_dotenv
import os
import nltk
from deepmultilingualpunctuation import PunctuationModel
import time
import scrapetube
import sys

# Load environment variables from .env file
load_dotenv()

# Check if the punkt tokenizer is already downloaded
if not nltk.data.find('tokenizers/punkt'):
    nltk.download('punkt')

# Access variables securely
LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo-1106')
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.openai.com/v1')
MAX_RETRIES = 5

async def generate_response(user_prompt, model, api_key, base_url="https://api.openai.com/v1", temperature=0.7):
    async_openai_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    for attempt in range(MAX_RETRIES):
        try:
            completion = await async_openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional transcript editor. You transform unformatted transcripts with bad or no punctuation, no formatting or just raw text, into perfectly formatted documents. You reformat text by removing and umms and ahmms, repeated words or rephrased words. Incorrectly placed punctuation, such as commas, semicolons, or periods, are removed. Uncessarily short sentences are merged. Return just the reformatted text, no labels, no titles, no headings, not a summary but only the full text. Keep the text and words as close to the original as possible without being gramartically incorrect. and avoid using synonymns or replacing words with similar words. Don't leave any notes,never ever say here is the reformatted text! no notes are required, infact, I hate notes! Just return any provided transcript perfectly formatted and ready to read."},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error generating response on attempt {attempt + 1}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1 * (2**attempt))
    return None

async def generate_transcript(video_id: str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(t['text'] for t in transcript)
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video {video_id}. Skipping...")
        return None

def punctuate_text(text):
    model = PunctuationModel()
    return model.restore_punctuation(text)

def find_sentence_boundaries(text):
    return nltk.sent_tokenize(text)

async def process_videos(channel_username, content_type="videos", sort_by="newest"):
    if content_type == "videos":
        videos = scrapetube.get_channel(channel_username=channel_username, content_type="videos", sort_by=sort_by)
    elif content_type == "streams":
        videos = scrapetube.get_channel(channel_username=channel_username, content_type="streams", sort_by=sort_by)
    else:
        vids = scrapetube.get_channel(channel_username=channel_username, content_type="videos", sort_by=sort_by)
        streams = scrapetube.get_channel(channel_username=channel_username, content_type="streams", sort_by=sort_by)
        videos = list(vids) + list(streams)

    videos = list(videos)  # Ensure videos is a list
    os.makedirs(f"transcripts/{channel_username}", exist_ok=True)
    print(f"Total videos found: {len(videos)}")

    for count, vid in enumerate(videos, start=1):
        video_title = vid['title']['runs'][0]['text']
        safe_video_title = video_title.replace('/', '-').replace('\\', '-') + ".txt"
        if safe_video_title in os.listdir(f"transcripts/{channel_username}"):
            print(f"Skipping {video_title} as it already exists.")
            continue
        print(f"Processing video ({count}/{len(videos)}): {video_title}")
        transcript = await generate_transcript(vid['videoId'])
        if transcript is None:
            continue

        transcript = punctuate_text(transcript)
        sentences = find_sentence_boundaries(transcript)

        #create 10 sentence chunks
        chunks = []
        for i in range(0, len(sentences), 10):
            chunks.append(' '.join(sentences[i:i+10]))
        

        for chunk in chunks:
            try:
                response = await generate_response(chunk, LLM_MODEL, API_KEY, BASE_URL, 0)
            except Exception as e:
                print(f"Failed to generate response: {e}")
                exit()
            # Write the response to a file named after the video ID in the transcripts folder and channel id folder
            with open(f"transcripts/{channel_username}/{safe_video_title}", "a") as file:
                if file.tell() == 0:  # Check if file is empty to write metadata at the top
                    #Write title and link  to file
                    file.write(f"Title: {video_title}\n")
                    file.write(f"Youtube URL: https://www.youtube.com/watch?v={vid['videoId']}\n")
                file.write(response + "\n")
                # indicate progress based on the number of chunks
                print(f"Progress: {chunks.index(chunk) + 1}/{len(chunks)}")

async def main():
    """
    Main function to handle user input and process video transcripts.
    """
    # Get username from command line argument or prompt user for input
    channel_username = sys.argv[1] if len(sys.argv) > 1 else input("Enter the channel username: ")
    
    # Prompt user to select content type and validate input
    prompt = """Please Choose your content type:
    1. Videos
    2. Streams
    3. Both
    Enter your choice: """
    user_choice = input(prompt)
    while user_choice not in ["1", "2", "3"]:
        user_choice = input(prompt)
    
    # Determine content type based on user choice
    content_type = "videos" if user_choice == "1" else "streams" if user_choice == "2" else "both"
    sort_by = "newest"
    await process_videos(channel_username, content_type, sort_by)
if __name__ == "__main__":
    asyncio.run(main())

