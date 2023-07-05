import praw
import os
import re
from gtts import gTTS
from moviepy.editor import*
import configparser

# TODO
# Filter out nsfw/bad words that the youtube algorithm would not like
# Filter out bot comments such as automod since it is irrelevant to the video
# Automate trimming the video such that the video is only as long as the audio clip 
# Display text using the strings generated such that users can follow along 

# Read the configuration from praw.ini
config = configparser.ConfigParser()
config.read('praw.ini')


# Authenticate with Reddit API using praw.ini
reddit = praw.Reddit("ytbot")


# Load Subway Surfers gameplay video and remove original audio
gameplay_video = VideoFileClip("sample_Trim.mp4")


# Get subreddit instance
# different subs you can use
# r/trueoffmychest
# r/confessions
# r/amitheasshole
# r/nostupidquestions
# r/tooafraidtoask
# r/showerthoughts
# r/todayilearned
subreddit = reddit.subreddit('todayilearned')

# Fetch hot posts from askreddit subreddit
hot_posts = subreddit.hot(limit=1)

# Function to sanitize the title for folder name
def sanitize_title(title):
    sanitized = re.sub(r'[<>:"/\\|?*]', ' ', title)  # Replace invalid characters with underscores
    sanitized = sanitized.strip()  # Remove leading/trailing whitespaces
    sanitized.replace(' ', '_')
    return sanitized

# Iterate over the posts and generate speech for the title and comments
for post in hot_posts:
    # Debug
    print(f"Title: {post.title}")

    # Create a folder for the post's title
    folder_name = sanitize_title(post.title)
    os.makedirs(folder_name, exist_ok=True)

    # Convert the title to speech using gTTS
    title_tts = gTTS(text=post.title, lang='en')

    # Save the title speech as an audio file
    title_audio_file = os.path.join(folder_name, f"post_{post.id}_title.mp3")
    title_tts.save(title_audio_file)

    # Load title audio file
    gp_audio = AudioFileClip(title_audio_file)

    # Fetch top-level comments
    top_comments = post.comments[:5] # Get the first 5 top comments
    # Print the top comments
    for comment in top_comments:
        # Debug
        print(f"Comment: {comment.body}")

        # Covert the comment to speech using gTTS
        comment_tts = gTTS(text=comment.body, lang='en')

        # Save the comment speech as an audio file
        comment_audio_file = os.path.join(folder_name, f"post_{post.id}_comment_{comment.id}.mp3")
        comment_tts.save(comment_audio_file)

        # Load the comment audio file
        comment_audio = AudioFileClip(comment_audio_file)

        # Splice the comment audio into the gameplay audio at the end
        gp_audio = concatenate_audioclips([gp_audio, comment_audio])

    # Remove the original audio from the gameplay video
    gameplay_video = gameplay_video.set_audio(None)

    # Set the new audio with the title and comments speech
    gameplay_video = gameplay_video.set_audio(gp_audio)

    # Save the final video with the replaced audio
    output_video = os.path.join(folder_name, "spliced_gameplay.mp4")
    gameplay_video.write_videofile(output_video, codec="libx264")

    # Debug
    print("Video generated and saved.")
    print("---------------")
