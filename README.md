# CSE408 Lyric Visualizer Demo


## Overview:
[Music visualization demo](https://youtu.be/su3WyCkIETI) constructed from a combination of animated lyrics and iTune's standard visualizer for the iconic song, "Africa" by Toto, created by Andrew Thomas for CSE408 MMIS final project.

I would like to credit to Carl von Bonin (@carl-vbn) who is the author of the original subtitle code that I modified to fit our visualization needs for the final project demo. Carl's original implementation, setup instructions, and general description are available at his [GitHub repository](https://github.com/carl-vbn/subtitle-generator) as well as demonstrated on his [YouTube channel](https://youtu.be/8yZ-x-WuFw0).


## How the Demo Works:
Unfortunately the original open-source tool, [Gentle](https://github.com/lowerquality/gentle) which automatically generated captions as well as their associated start and end times based upon a provided transcript, failed to identify all the lyrics and times. As a result, captions were generated manually with lyrics downloaded from the Genius API instead. A specialized JSON format was used to encapsulate each caption's lyric content as well as their start and end times to improve audio alignment accuracy.

Animated captions consisted of parsing caption information from the specialized JSON file and programmatically generating frames which display lyrics at the appropriate times in the visualization. Frame generation was accomplished using a modified version of the Python script originally developed by author Carl von Bonin.

After the generation process, caption frames are then converted into video format, overlaid onto the visualization video, and combined with music audio to produce a single output video using the [ffmeg-python wrapper](https://github.com/kkroening/ffmpeg-python) for the open-source FFmpeg tool. The resulting output video consists of abstract music visualization, animated lyrics, and audio all synchronized together to provide a unique music visualization experience similar to that of karaoke.


## Running the Demo:
1. Clone this GitHub repository
2. Download [FFmpeg](https://www.ffmpeg.org/download.html) for your OS and follow the installation guide
   * If you're using a Mac, download a static build, unzip the file, and copy the **ffmpeg binary** into your ```/usr/local/bin``` directory
3. Open a terminal or IDE and run the command ```pip install ffmpeg-python```
4. In the same terminal or IDE, run the command ```pip install Pillow```
5. Download the required video files available at this [Google Drive folder](https://drive.google.com/drive/folders/1FkWSY-HvCIxcB460NIJnvaL5N91FXyni?usp=sharing)
   * Please ensure these video files are copied into the directory where you cloned this repository
6. Open a terminal or IDE in the directory where you cloned this repository and run the command ```python visualizer.py```


## Warning:
Generating the caption frames as well as compiling the final output video is extremely CPU intensive and could take up to 30 minutes to complete depending upon your computer specifications when running ```visualizer.py```.
