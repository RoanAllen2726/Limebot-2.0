import asyncio
from twitchio.ext import commands
import subprocess
import moviepy.editor as mp
import speech_recognition as sr
from pydub import AudioSegment
import os


# Function to capture a 5-second Twitch stream clip
def capture_twitch_clip(stream_url, output_file, duration=5):
    try:
        streamlink_cmd = ['streamlink', stream_url, 'best', '--hls-duration', str(duration), '-o', output_file]
        print(f"Executing command: {' '.join(streamlink_cmd)}")
        
        result = subprocess.run(streamlink_cmd, check=True, capture_output=True, text=True)
        print(f"Streamlink output: {result.stdout}")
        print(f"Streamlink errors: {result.stderr}")
        return output_file
    except FileNotFoundError:
        print("Error: Streamlink executable not found. Ensure it's installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Function to extract audio from the video clip
def extract_audio_from_video(video_file, audio_output_file):
    """
    Extract audio from a video clip and save it as an MP3.
    """
    try:
        video = mp.VideoFileClip(video_file)
        video.audio.write_audiofile(audio_output_file)
        video.close()  # Ensure the video file is closed after processing
        print(f"Audio file saved at: {audio_output_file}")
    except Exception as e:
        print(f"Error extracting audio: {e}")


# Function to convert audio format
def convert_audio_format(file_path, output_format="wav"):
    audio = AudioSegment.from_file(file_path)
    output_file = "converted_audio." + output_format
    audio.export(output_file, format=output_format)
    return output_file

def transcribe_audio(audio_file, language="en-US"):
    recognizer = sr.Recognizer()
    
    # Ensure the file exists
    if not os.path.isfile(audio_file):
        return f"Error: File {audio_file} does not exist."
    
    # If audio is not in wav format, convert it
    if not audio_file.endswith(".wav"):
        audio_file = convert_audio_format(audio_file)
    
    if not audio_file:
        return "Error: Could not convert audio."

    # Ensure the converted file exists
    if not os.path.isfile(audio_file):
        return f"Error: Converted file {audio_file} does not exist."

    # Load the audio file and try to recognize it
    try:
        with sr.AudioFile(audio_file) as source:
            recognizer.adjust_for_ambient_noise(source)  # Adjust for noise levels in the file
            audio_data = recognizer.record(source)
        
        # Recognize the speech in the audio using Google API
        text = recognizer.recognize_google(audio_data, language=language)
        return text
    
    # Handle errors in recognition
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        return f"Could not request results; {e}"
    except Exception as e:
        return f"Error during transcription: {e}"

# Main function to capture and transcribe a single 5-second clip
def main():
    stream_url = "https://www.twitch.tv/erobb221"  # Replace with your Twitch channel URL
    video_file = "twitch_clip.mp4"
    audio_file = "twitch_audio.mp3"
    clip_duration = 10  # Capture 5-second clips

    # Step 1: Capture a 5-second Twitch stream clip
    print(f"Capturing a 5-second clip...")
    captured_video = capture_twitch_clip(stream_url, video_file, duration=clip_duration)

    if captured_video is None or not os.path.isfile(video_file):
        print(f"Error: Video file {video_file} was not created.")
        return

    # Step 2: Extract audio from the video clip
    print(f"Extracting audio from the clip...")
    extract_audio_from_video(video_file, audio_file)

    if not os.path.isfile(audio_file):
        print(f"Error: Audio file {audio_file} was not created.")
        return

    # Step 3: Transcribe the audio
    print(f"Transcribing the audio...")
    transcription = transcribe_audio(audio_file)
    if transcription != None:
        bot = TwitchBot()
        # Start the Twitch bot and the test message loop
        bot.loop.create_task(send_test_message(bot, transcription))
        bot.run()
    if transcription == None:
        print("Couldnt Transcibe")

    # Clean up the video and audio files to save disk space
    try:
        os.remove(video_file)
        os.remove(audio_file)
    except PermissionError as e:
        print(f"Error deleting file: {e}")


# Twitch bot class to handle chat messages
class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token='oauth:8iioachuzqm2rbwtn50levxrz9p69p', prefix='!', initial_channels=['robo2726'])
        self.channel = None  # Initialize self.channel as None

    async def event_ready(self):
        print(f'Logged in as {self.nick}')
        print(f'Connected to channel {self.connected_channels}')

        # Retrieve the channel object and store it in self.channel
        self.channel = self.get_channel('robo2726')
        if self.channel:
            print(f'Channel {self.channel.name} is ready for messages!')

    async def event_message(self, message):
        # Ensure the message has an author before processing
        if message.author and message.author.name.lower() == 'limebot2726':
            return  # Ignore messages from the bot itself

    async def send_chat_message(self, message):
        # Ensure that the channel object is available before sending messages
        if self.channel is not None:
            await self.channel.send(message)
        else:
            print("Channel is not ready yet.")



if __name__ == '__main__':
    main()
    # Function to send a test message without capturing audio
    async def send_test_message(bot, message):
        await bot.wait_for_ready()  # Wait until the bot is connected and ready
        while True:
            print(f"Sending: {message}")
            await bot.send_chat_message(message)
            await asyncio.sleep(300)
            main()
            # Wait for 10 seconds (or 300 seconds for 5 minutes) before sending again
            
