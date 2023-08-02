# Import the Pytube module
from pytube import YouTube

# Prompt the user for the video URL
url = input("Enter the YouTube video URL: ")

# Create a YouTube object with the URL
video = YouTube(url)

# Get the highest resolution stream available
stream = video.streams.get_highest_resolution()

# Get the last 3 characters of the URL
suffix = url[-3:]

# Download the video as a .mp4 file with the suffix
stream.download(output_path="C:\\Users\\Keigan\\Desktop\\TEST LOGIC FOLDER", filename=f"video{suffix}.mp4")

# Alternatively, download the video as a .mov file with the suffix
# stream.download(output_path="C:\\Users\\Desktop", filename=f"video{suffix}.mov")

# Print a message when done
print("Download completed!")

