#!/usr/bin/env python

import assemblyai as aai
import av
import os
import cv2
import sys
from moviepy import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm
from config import assemblyai_api_key

aai.settings.api_key = assemblyai_api_key # linked to my assemblyai account - google: brendanrboone@gmail.com

class VideoTranscriber:
    def __init__(self, video_path, maxcap, font, font_size, color, yaxis, rotate):
        self.video_path = video_path
        self.transcriber = aai.Transcriber()
        self.audio_path = ''
        self.text_array = []
        self.fps = 0
        self.maxcap = maxcap
        self.char_width = 0
        self.font = font
        self.font_size = font_size
        self.color = color
        self.yaxis = yaxis # percentage wraps around if exceeds 100
        self.rotate = rotate # 90deg segments [1-3]
        self.width = 0
        self.height = 0
        self.asp = 0
        if not os.path.exists("outputFiles"):
            os.makedirs("outputFiles")

    def get_video_rotation(self, video_path):
        with av.open(video_path) as container:
            stream = container.streams.video[0]
            print(stream)
            if hasattr(stream, 'metadata') and 'rotate' in stream.metadata:
                return int(stream.metadata['rotate'])
        return 0

    def transcribe_video(self):
        print('Transcribing video')
        transcript = self.transcriber.transcribe(self.audio_path)
        
        # Get the first word's text as initial text for size calculation
        text = transcript.words[0].text if transcript.words else ""
        textWidth, _ = cv2.getTextSize(text, self.font, self.font_size, 2)[0]
        cap = cv2.VideoCapture(self.video_path)
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.asp = self.width / self.height
        
        ret, frame = cap.read()
        for _ in range(self.rotate):
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        print("FRAME\n", frame.shape)
        
        videoWidthLimit = frame.shape[1] - (frame.shape[1] * 0.1)  # WIDTH LIMIT IN PIXELS
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.char_width = int(textWidth/len(text)) if text else 1

        words = tqdm(transcript.words)
        print("\n")

        current_utterance = [] # [current_line, start, end]
        current_width = 0
        current_line = ""
        current_wc = 0         # word count
        start = 0
        end = 0
        ending_delay = 10      # add an arbitrary delay at the end *in frames
        for i, word in enumerate(words):
            print(i, word, "!")
            if start == 0: start = word.start / 1000 * self.fps
            end = word.end / 1000 * self.fps
            wordWidth, _ = cv2.getTextSize(word.text, self.font, self.font_size, 2)[0]
            current_wc += 1
            if current_width + wordWidth < videoWidthLimit and current_wc <= self.maxcap:
                current_line += word.text + " "
                current_width += wordWidth + 1
            else:
                if current_width != 0: current_line = current_line[:-1] # removes the last space
                else: print("ERROR: text too big", file=sys.stderr)
                time_of_next_word = word.start / 1000 * self.fps # subtitle prioritizes start timing
                current_utterance = [current_line, start, time_of_next_word]
                print("current utterance:", current_utterance)
                self.text_array.append(current_utterance)
                current_wc = 1
                start = word.start / 1000 * self.fps
                current_line = word.text + " "
                current_width = wordWidth + 1
        current_utterance = [current_line, start, end + ending_delay]
        self.text_array.append(current_utterance)

        cap.release()
        print('Transcription complete')

    def extract_audio(self, output_audio_path='outputFiles/audio.mp3'):
        print('Extracting Audio')
        video = VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)
        self.audio_path = output_audio_path
        print('Audio extracted')
    
    def extract_frames(self, output_folder):
        print('Extracting frames')
        cap = cv2.VideoCapture(self.video_path)
        N_frames = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            for _ in range(self.rotate):
                frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

            # SUBTITLING HERE -- utterance: [current_line, start, end]
            for utterance in self.text_array:
                if N_frames >= utterance[1] and N_frames <= utterance[2]:
                    text = utterance[0]
                    text_size, _ = cv2.getTextSize(text, self.font, self.font_size, 2)
                    text_x = int((frame.shape[1] - text_size[0]) / 2)
                    text_y = int(frame.shape[0] * (self.yaxis/100))
                    cv2.putText(frame, text, (text_x, text_y), self.font, self.font_size - 0.05, self.color, 2)
                    break
        
            cv2.imwrite(os.path.join(output_folder, str(N_frames) + ".jpg"), frame)
            N_frames += 1
        
        cap.release()
        print('Frames extracted')

    def create_video(self, output_video_path):
        print('Creating video')
        image_folder = os.path.join("outputFiles/", "frames")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        else:
            # Remove all files in the existing folder
            for file in os.listdir(image_folder):
                file_path = os.path.join(image_folder, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'Error deleting {file_path}: {e}')

        self.extract_frames(image_folder)

        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))

        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=self.fps)
        audio = AudioFileClip(self.audio_path)
        clip = clip.with_audio(audio)
        clip.write_videofile(output_video_path)

