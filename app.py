from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
import asyncio
import os
import sys
import scrapetube

async def generate_transcript(video_id: str) -> str:
    """
    Fetches and concatenates the transcript for a given YouTube video ID.
    
    Args:
    video_id (str): The YouTube video ID.
    
    Returns:
    str: The full transcript as a single string or None if transcripts are disabled.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(t['text'] for t in transcript)
    except TranscriptsDisabled:
        print(f"Transcripts are disabled for video {video_id}. Skipping...")
        return None

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
    
    # Fetch videos based on user choice
    if user_choice == "1":
        videos = scrapetube.get_channel(channel_username=channel_username, content_type="videos", sort_by="newest")
    elif user_choice == "2":
        videos = scrapetube.get_channel(channel_username=channel_username, content_type="streams", sort_by="newest")
    else:
        vids = scrapetube.get_channel(channel_username=channel_username, content_type="videos", sort_by="newest")
        streams = scrapetube.get_channel(channel_username=channel_username, content_type="streams", sort_by="newest")
        videos = list(vids) + list(streams)
    
    # Ensure videos is a list
    videos = list(videos)
    print("Total videos found:", len(videos))
    
    # Create directory for transcripts
    os.makedirs(f"transcripts/{channel_username}", exist_ok=True)
    
    # Process each video
    for count, vid in enumerate(videos, start=1):
        vid_id = vid['videoId']
        video_title = vid['title']['runs'][0]['text']
        safe_video_title = video_title.replace('/', '-').replace('\\', '-') + ".txt"
        
        # Skip if transcript file already exists
        if safe_video_title in os.listdir(f"transcripts/{channel_username}"):
            print(f"Skipping {video_title} as it already exists in transcripts folder")
            continue
        
        print(f"Generating transcript for video ({count}/{len(videos)}):", video_title)
        transcript = await generate_transcript(vid_id)
        if transcript is None:
            continue  # Skip if no transcript available
        
        # Write transcript to file
        with open(f"transcripts/{channel_username}/{safe_video_title}", "w") as file:
            file.write(transcript)

if __name__ == "__main__":
    asyncio.run(main())
