# CSE 408 FINAL PROJECT: MUSIC LYRICS VISUALIZER
# ANDREW THOMAS
# 1215343233
# 11/22/21

from PIL import Image, ImageDraw, ImageFont
from math import *

import os
import ffmpeg
import json

currentIndex = 0

# IMAGE INFO:
WIDTH = 1280
HEIGHT = 702
FRAMERATE = 60
FONT = ImageFont.truetype('ChalkboardSE.ttc', 36)

# FRAME INFO:
STARTFRAME = 0
ENDFRAME = -1

# CAPTION INFO:
OUTLINE_SIZE = 4
SUBTITLE_HEIGHT = 100
MAX_SUBTITLE_DURATION = 3
MAX_WORD_DURATION = 0.6
MAX_SUBTITLE_WIDTH = 900

# BACKGROUND INFO:
OUTLINE_COLOR = (0, 0, 0, 255)
TEXT_COLOR = (255, 255, 255, 255)
IMAGE_SEQUENCE_OUTPUT_DIRECTORY = "generated_image_sequence"


#----------------------------------------------------------------------------------------------------------------------------
# If we want to overlay the subtitles on top of the input video, the base has to be fully transparent
base = Image.new('RGBA', (WIDTH, HEIGHT), (0,0,0,0))


# MAKE SURE SEQUENCE DIRECTORY IS DELETED BEFORE RUNNING AGAIN!
os.makedirs(IMAGE_SEQUENCE_OUTPUT_DIRECTORY)


# GENERATES TEXT SEQUENCES WHICH ARE APPLIED ONTO THE TRANSPARENT BASE IMAGE
def generate_text_image(text, scale=1):
    txt_size = FONT.getsize(text)
    txt_img = Image.new('RGBA', (txt_size[0]+OUTLINE_SIZE*2, txt_size[1]+OUTLINE_SIZE*2), (0,0,0,0))

    draw = ImageDraw.Draw(txt_img)

    # Draw outline
    for i in range(100):
        angle = i/100*(2*pi)
        draw.text((OUTLINE_SIZE+sin(angle)*OUTLINE_SIZE, OUTLINE_SIZE+cos(angle)*OUTLINE_SIZE), text, font = FONT, fill = OUTLINE_COLOR)

    # Draw text itself
    draw.text((OUTLINE_SIZE, OUTLINE_SIZE), text, font = FONT, fill = TEXT_COLOR)

    if scale == 1:
        return txt_img
    
    else:
        txt_img = txt_img.resize((floor(txt_img.size[0]*scale), floor(txt_img.size[1]*scale)), Image.ANTIALIAS)
        return txt_img


# USED TO CREATE THE "BOUNCE" ANIMATION THAT TEXT HAS WHEN COMING ONTO THE SCREEN
def get_text_scale_at_frame(start_time, frame):
    frame_time = frame/FRAMERATE
    x = frame_time - start_time
    scale = -(x*7-1)**2+1.1 # Upside-down parabola
    if x > 0.2:
        scale = max(scale, 1)
    
    return scale


# RETURNS THE INDEX OF THE CAPTION TEXT THAT SHOULD BE PRESENT ON A SPECIFIC FRAME.
def get_caption_at_frame(subtitles, starts, ends, frame):
    global currentIndex
    
    frame_time = round((frame/FRAMERATE),2)
    #print(f'Current frame: {frame_time}')

    if(currentIndex < len(subtitles)):
        if(starts[currentIndex] <= frame_time < ends[currentIndex]):
            #print(f'{subtitles[currentIndex]} starts: {starts[currentIndex]} | ends: {ends[currentIndex]}')
            return currentIndex
        elif(ends[currentIndex] == round(frame_time,1)):
            currentIndex += 1
            return None
        else:
            #print(f'No in between for {frame_time}')
            return None
    else:
        #print(f'No in between for {frame_time}')
        return None


#----------------------------------------------------------------------------------------------------------------------------
# GET ALL THE LYRIC CAPTIONS FROM THE JSON FILE
print('Start processing captions...')
with open("captions_demo.json","r") as file:
    captions = file.read()

captions_info = json.loads(captions)
allCaptions = captions_info["captions"]
numCaptions = len(allCaptions)
print(f'Total number of captions = {numCaptions}')


# LISTS TO STORE ALL CAPTIONS AS WELL AS THEIR START AND END TIMES
subtitles = []
starts = []
ends = []

# PREPROCESS CAPTION INFORMATION AND POPULATE THE LISTS WITH THEIR DATA
for index in range(len(allCaptions)):
    
    caption = allCaptions[index]
    
    caption_start = caption["start"]
    caption_end = caption["end"]
    caption_text = caption["caption"]

    print(f'[{caption_start}--> {caption_end}] {caption_text}')

    if(FONT.getsize(caption_text)[0] >= MAX_SUBTITLE_WIDTH):
        print(f'Caption \"{caption_text}\" greater than the line size...')
    else:
        starts.append(caption_start)
        ends.append(caption_end)
        subtitles.append(caption_text)


#----------------------------------------------------------------------------------------------------------------------------
# GENERATE AN IMAGE SEQUENCE CONTAINING SYNCED SUBTITLES USING THEIR START AND END TIMES
print('Translating subtitles into image sequence...')

frame_count = floor((ends[-1]+MAX_SUBTITLE_DURATION)*FRAMERATE)

# Clamp Start/end frame args
start_frame = min(frame_count, max(0, STARTFRAME))

if ENDFRAME < 0:
    end_frame = frame_count-1
else: 
    end_frame = min(frame_count, max(start_frame, ENDFRAME))


# GENERATES ALL OF THE FRAMES WHICH WILL GET CONVERTED INTO A VIDEO OVERLAY OF SYNCHRONIZED LYRICS
for frame in range(start_frame, end_frame+1):
    subtitle_index = get_caption_at_frame(subtitles, starts, ends, frame)

    img = base.copy()
    if subtitle_index is not None:
        subtitle = subtitles[subtitle_index]
        start_time = starts[subtitle_index]
        txt_img = generate_text_image(subtitle, scale=get_text_scale_at_frame(start_time, frame))
        img.paste(txt_img, (floor(base.size[0]/2-txt_img.size[0]/2), floor(HEIGHT-SUBTITLE_HEIGHT-txt_img.size[1]/2)))

    img.save(os.path.join(IMAGE_SEQUENCE_OUTPUT_DIRECTORY, "frame_"+str(frame)+".png"), "PNG")


print("Subtitle image sequence successfully compiled.")


#----------------------------------------------------------------------------------------------------------------------------
# COMBINE GENERATED CAPTION FRAMES WITH VIDEO AND AUDIO TO PRODUCE CAPTIONED VISUALIZATION
baseFile = ffmpeg.input('visual_demo.mp4')
overlayFile = ffmpeg.input(IMAGE_SEQUENCE_OUTPUT_DIRECTORY+'/frame_%d.png', framerate = FRAMERATE)
audioFile = ffmpeg.input('africa_demo.mp4')
(
    ffmpeg
    .filter([baseFile,overlayFile], 'overlay', 10, 10)
    # having the audioFile['1'] as the first parameter indicates that audio
    # from the audioFile will be mapped/applied to the ouput file produced.
    .output(audioFile['1'], 'final_demo.mp4') # maps audio from africa_demo.mp4 to the output file.
    .run()
)


#----------------------------------------------------------------------------------------------------------------------------
# OLD CODE THAT WAS USED FOR FFMPEG TESTING AND GETTING LYRICS
'''
# this sequence of commands combines both the overlay frames with the main video and
# applies the audio from the main video as the audio of the output video.
# https://codingshiksha.com/python/python-3-ffmpeg-example-to-add-overlay-or-logo-image-to-video-using-ffmpeg-python-library-full-project-for-beginners/
# https://github.com/kkroening/ffmpeg-python/issues/102
baseFile = ffmpeg.input("africa_demo.mp4")
overlayFile = ffmpeg.input(IMAGE_SEQUENCE_OUTPUT_DIRECTORY+'/frame_%d.png', framerate = 24)
(
    ffmpeg
    .filter([baseFile,overlayFile], 'overlay', 10, 10)
    .output(baseFile['1'], "testing.mp4")
    .run()
)

tokens = {
    "clientID" : "znHspY84yoNPiHyK1EitvMK9FZjJJWDAYIkRP7-MOH0mQRE1ZYOSXi9CUmHlDnTA",
    "secretKey" : "duiJ38runGaCKObbIqAQZDY0doz4puUdBxbvBRjYa_F13WD_5dwo9GUJXhr7XWX5d5ZDJv6OoyY_JWljNoct3w",
    "accessToken" : "12BWc57-0c55ajmZfA5yTA78spI-4lhHyVvUouOpV_4DAkyiDqm0zcjdd8rdV7jN",
}

# https://towardsdatascience.com/song-lyrics-genius-api-dcc2819c29
# Old stuff to download lyrics from Genius API
import lyricsgenius as lg

genius = lg.Genius(access_token=token, excluded_terms=["(Remix)","(Live)"], remove_section_headers=True)

artist = genius.search_artist(artist_name="Toto", max_songs=1, sort="popularity")

# print out the top 4 songs by Childish Gambino ranked by popularity
#print(targetArtist.songs)
#artist.add_song("Never Gonna Give You Up")
song = artist.song("Africa")
lyrics = song.lyrics

with open("song_lyrics_transcript.txt", "w") as transcript:
    i = lyrics.index("EmbedShare") - 3  # to account for weird embed text leftover
    lyrics = lyrics[:i]
    transcript.write(lyrics)
    transcript.close()
'''
