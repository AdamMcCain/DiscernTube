# DiscernTube, v0.94 (Beta), 1/22/2024
# Takes in a YouTube URL via command line argument and speaks a summary of the video's spoken content
# Can also be used to print / send summary to stdout instead of speaking it (enables piping)
# Example usage: python3 summarize.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
# A project by Adam McCain, initial release 1/20/2024

from pytube import YouTube
from openai import OpenAI
import ssl
import sys
import platform
import time
import subprocess
import os
import system_message
from app_secrets import openai_api_key

# True to create audio from summary, False to print summary text / send to stdout
SPEAK_SUMMARY = True

# Initialize OpenAI client with API key
client = OpenAI(api_key=openai_api_key)

# Disable SSL verification warning (Warning: Vulnerable to MITM attacks)
ssl._create_default_https_context = ssl._create_unverified_context

# System message setup for GPT
message_chain = [
    {"role": "system", "content": system_message.system_message.strip()}
]

# Model choices for OpenAI API
gpt_model_choices = {
    'best': 'gpt-4-1106-preview',  # Expensive, 128k context window for long videos
    'good': 'gpt-3.5-turbo-16k'    # Low cost, 16k context window
}

# Choosing the OpenAI model (use best for long videos and/or more accurate results)
model = gpt_model_choices['good']

# Function to verify platform type
def os_type():
    os_type = platform.system()
    if os_type == 'Darwin':
        return 'macOS'
    elif os_type == 'Linux':
        return 'Linux'
    elif os_type == 'Windows':
        return 'Windows'
    else:
        return 'Unknown'

# Function to delete a file
def delete_file(file_path):
    """Delete a file at the specified path."""
    try:
        os.remove(file_path)
    except OSError as e:
        pass

# Function to summarize the transcript
def do_summary(user_input):
    """Obtain transcript summary using OpenAI GPT API."""
    new_message = {
        "role": "user",
        "content": '<BEGIN TRANSCRIPTION FROM VIDEO\'s AUDIO>' + user_input + '<BEGIN TRANSCRIPTION FROM VIDEO\'s AUDIO>'
    }
    message_chain.append(new_message)

    while True:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=message_chain,
                temperature=0.7,
                max_tokens=4096,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response.choices[0].message.content
        except Exception as e:
            print('GPT API Error: ', end='')
            print(e)
            time.sleep(5)

# Function to download audio from YouTube video
def download_audio(youtube_url, output_path):
    """Download audio from a YouTube video using pytube.
    Tries to download in WEBM format, defaults to the first available audio format if WEBM is not available."""
    try:
        yt = YouTube(youtube_url)
        # First, try to get WEBM audio format
        audio_stream = yt.streams.filter(only_audio=True, file_extension='webm').first()
        
        # If no WEBM audio stream is available, default to the first available audio stream
        if not audio_stream:
            audio_stream = yt.streams.filter(only_audio=True).first()
            if not audio_stream:
                print("No audio stream available.")
                return None

        return audio_stream.download(output_path=output_path)
    except Exception as e:
        print('pytube Error: ', end='')
        print(e)
        return None

# Function to convert audio to text
def make_transcription(audio_path):
    """Convert audio to text using OpenAI Whisper API."""
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print('Whisper API Error: ', end='')
        print(e)
        return None

# Function to speak text summary
def speak_text(text):
    """Convert text to speech using OpenAI TTS API or output to stdout."""
    if SPEAK_SUMMARY:
        try:
            speech_file_path = "transcript_summary.mp3"
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            response.stream_to_file(speech_file_path)
            print('\n\t' + text + '\n')

            current_os = os_type()
            if current_os == 'macOS':
                subprocess.run(["afplay", speech_file_path])
            elif current_os == 'Windows':
                subprocess.run(["start", speech_file_path], shell=True)
            elif current_os == 'Linux':
                subprocess.run(["xdg-open", speech_file_path])
            else:
                print(f"Unsupported operating system, please open the audio file manually ({speech_file_path}).")
        except Exception as e:
            print('TTS API Error: ', end='')
            print(e)
    else:
        # If SPEAK_SUMMARY is False, output sumary as text
        print(text)


# Main program
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)

    youtube_url = sys.argv[1]
    output_path = '.'

    audio_file_path = download_audio(youtube_url, output_path)
    print('Analyzing video...')
    if not audio_file_path:
        sys.exit(1)

    transcript = make_transcription(audio_file_path)
    if not transcript:
        sys.exit(1)

    if audio_file_path != 'transcript_summary.mp3':
        delete_file(audio_file_path)

    gpt_response = do_summary(transcript)
    if not gpt_response:
        sys.exit(1)

    if SPEAK_SUMMARY:
        speak_text(gpt_response)
    else:
        print(gpt_response)