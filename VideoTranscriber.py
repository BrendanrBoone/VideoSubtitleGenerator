#!/usr/bin/env python

import assemblyai as aai
import os
import cv2
from moviepy import ImageSequenceClip, AudioFileClip, VideoFileClip
from tqdm import tqdm
from config import assemblyai_api_key

aai.settings.api_key = assemblyai_api_key # linked to my assemblyai account - google: brendanrboone@gmail.com

class VideoTranscriber:
    def __init__(self, video_path):
        self.video_path = video_path
        self.transcriber = aai.Transcriber()
        self.audio_path = ''
        self.text_array = []
        self.fps = 0
        self.char_width = 0

    def transcribe_video(self):
        print('Transcribing video')
        transcript = self.transcriber.transcribe(self.audio_path)
        
        # Get the first word's text as initial text for size calculation
        text = transcript.words[0].text if transcript.words else ""
        textWidth, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = 16/9
        ret, frame = cap.read()
        width = frame[:, int(int(width - 1/asp * height) / 2):width - int((width - 1/asp * height) / 2)].shape[1]
        videoWidthLimit = width - (width * 0.1) # WIDTH LIMIT IN PIXELS
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.char_width = int(textWidth/len(text)) if text else 1

        words = tqdm(transcript.words)
        print("\n")

        current_utterance = [] # [current_line, start, end]
        current_width = 0
        current_line = ""
        start = 0
        end = 0
        for i, word in enumerate(words):
            print(i, word, "!")
            if start == 0: start = word.start / 1000 * self.fps
            end = word.end / 1000 * self.fps
            wordWidth, _ = cv2.getTextSize(word.text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            if current_width + wordWidth < videoWidthLimit:
                current_line += word.text + " "
                current_width += wordWidth + 1
            else:
                if current_width != 0: current_line = current_line[:-1] # removes the last space
                time_of_next_word = word.start / 1000 * self.fps # subtitle start priority in timing
                current_utterance = [current_line, start, time_of_next_word]
                print("current utterance:", current_utterance)
                self.text_array.append(current_utterance)
                start = word.start / 1000 * self.fps
                current_line = word.text + " "
                current_width = wordWidth + 1
        current_utterance = [current_line, start, end]
        self.text_array.append(current_utterance)

        cap.release()
        print('Transcription complete')

    def extract_audio(self, output_audio_path='testMP4Files/audio.mp3'):
        print('Extracting Audio')
        video = VideoFileClip(self.video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path)
        self.audio_path = output_audio_path
        print('Audio extracted')
    
    def extract_frames(self, output_folder):
        print('Extracting frames')
        cap = cv2.VideoCapture(self.video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        asp = width / height
        N_frames = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = frame[:, int(int(width - 1 / asp * height) / 2):width - int((width - 1 / asp * height) / 2)]

            # SUBTITLING HERE -- utterance: [current_line, start, end]
            for utterance in self.text_array:
                if N_frames >= utterance[1] and N_frames <= utterance[2]:
                    text = utterance[0]
                    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                    text_x = int((frame.shape[1] - text_size[0]) / 2)
                    text_y = int(height/2)
                    cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                    break
        
            cv2.imwrite(os.path.join(output_folder, str(N_frames) + ".jpg"), frame)
            N_frames += 1
        
        cap.release()
        print('Frames extracted')

    def create_video(self, output_video_path):
        print('Creating video')
        image_folder = os.path.join(os.path.dirname(self.video_path), "frames")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        self.extract_frames(image_folder)

        images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
        images.sort(key=lambda x: int(x.split(".")[0]))

        clip = ImageSequenceClip([os.path.join(image_folder, image) for image in images], fps=self.fps)
        audio = AudioFileClip(self.audio_path)
        clip = clip.with_audio(audio)
        clip.write_videofile(output_video_path)

