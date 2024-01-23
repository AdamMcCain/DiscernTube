"""
# DiscernTube: YouTube Video Summarization Tool

## Overview
DiscernTube is a Python script designed to summarize YouTube videos, to your liking. It can either vocalize the summary or output it as text for further processing/piping. Its analysis is purely based on the video's audio content, it does not analyze visuals.

## Initial Setup
Before using DiscernTube, an OpenAI API key is required. Place your API key in the app_secrets.py file:

openai_api_key = "YOUR_API_KEY_HERE"

## Installation
Ensure Python 3 and necessary packages (pytube, openai) are installed:

On most systems this can be done using the "pip install -r requirements.txt" command (use pip3 on macOS)

## Usage
Run DiscernTube with a YouTube URL:

python DiscernTube.py "YOUTUBE_VIDEO_URL"

### Customizing System Messages for Tailored Output
To tailor the summary queries, modify the system_message.py file. This file should contain prompts that instruct the AI on what to focus on, such as:
- Key takeaways from the video.
- The intended audience for the content.
- Whether the content is suitable for minors.

Example system_message.py:

system_message = """

You summarize YouTube videos for the user. The only user input you are given is a complete transcription of the video's audio content, and the user is unable to add anything additional. The summaries you provide then get spoken to the user using openAI TTS (text to speech) so use a natural spoken tone in your text output. The only thing you shall output is the summary/explanation, nothing more. Focus your takeaways on areas relating to strategic security leadership if there are any. And of course, cats. Use humor in your summary but do not fudge the facts. You always begin by saying "What I discerned from this video's audio track..."

"""

### Advanced Options
1. Speak Summary: Set SPEAK_SUMMARY to True or False in the script for vocal or text output.
2. Model Choice: Choose between 'best' and 'good' models in the script for different levels of detail and cost efficiency.

### Piping Output
If SPEAK_SUMMARY is set to False, the output can be piped into other commands like so:

python3 DiscernTube.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" | cat > video_summary.txt

"""

## Known Issues
25 MB max file size (typically correlates to about 1 hour long videos)

## Change Log
v0.93 - Now defaults to WEBM audio format

v0.94 - More detailed output