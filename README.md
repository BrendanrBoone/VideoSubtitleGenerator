# Video Subtitle Generator
Generates subtitles for given mp4 file. If file name is not specified, records audio live

* Uses AssemblyAI to transcribe speech

## Requirment
* make an api key with [assemblyai](https://www.assemblyai.com/dashboard/api-keys?project=526016)

## Setup
* replace ```assemblyai_api_key``` with the one created above
* ```pip install opencv-python assemblyai moviepy tqdm numpy sounddevice argparse```

## Usage

```python main.py [-h] [-f FILE] [-m MAXCAP] [-F FONT] [-S FONT_SIZE] [-c COLOR] [-y YAXIS] [-r ROTATE]```

### font options:
* 'simplex'
* 'plain'
* 'duplex'
* 'complex'
* 'triplex'
* 'complex_small'
* 'script_simplex'
* 'script_complex'
* 'italic'
### color options:
* 'white'
* 'black'
* 'red'
* 'green'
* 'blue'
* 'yellow'
* 'cyan'
* 'magenta'
* 'gray'
* 'dark_gray'
* 'light_gray'
* 'orange'
* 'purple'
* 'pink'
* 'brown'
* 'navy'
* 'lime'
* 'teal'

## Things to do
* implement video transcriber to ui
* add frames folder for sub imp on ui
* video transcriber when running app.py
* someway around cv2 base font scale and css font point
* resizable textbox
* implement text editing feature - likely by producing trancript file additionally to the generated video
* add like a shadow, and maybe cycling colors for text