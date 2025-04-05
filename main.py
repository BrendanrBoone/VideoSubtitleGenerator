#!/usr/bin/env python

import assemblyai as aai
import argparse
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import sys
from config import assemblyai_api_key
from VideoSubtitleGenerator.util.video_transcriber import VideoTranscriber
from VideoSubtitleGenerator.util.font import Fonts
from VideoSubtitleGenerator.util.colors import Colors

aai.settings.api_key = assemblyai_api_key
transcriber = aai.Transcriber()

SAMPLE_RATE = 16000
CHUNK_DURATION = 5

def saveAudioChunk(audio_data, sample_rate):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wav_file.writeframes(audio_int16.tobytes())
        return temp_file.name

def recordAudio():
    print("Listening... (Press Ctrl+C to stop)")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32') as stream:
        while True:
            audio_chunk, _ = stream.read(int(SAMPLE_RATE * CHUNK_DURATION))
            audio_np = np.squeeze(audio_chunk)
            temp_file = saveAudioChunk(audio_np, SAMPLE_RATE)
            try:
                transcript = transcriber.transcribe(temp_file)
                print("Transcription:", transcript.text)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
            finally:
                os.unlink(temp_file)

# reads inputted file. The file can be any common sound or video file (e.g. mp3, mp4, etc)
# @param file: str
# @param maxcap: int
def transcriptFile(file, maxcap, font, font_size, color, yaxis, rotate):
    try:
        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):  # Video files
            transcriber = VideoTranscriber(file, maxcap, font, font_size, color, yaxis, rotate)
            transcriber.extract_audio()
            transcriber.transcribe_video()
            # Generate output path in same directory as input
            output_path = os.path.join('outputFiles/', 'output_' + os.path.basename(file))
            transcriber.create_video(output_path)
        else:  # Audio files
            transcript = transcriber.transcribe(file)
            if transcript.status == aai.TranscriptStatus.error:
                print(transcript.error)
            else:
                print(transcript.text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

# depending if file was inputed, records audio or reads inputted file
# @param file: str
# @param maxcap: int
def transcriptAudio(file, maxcap, font, font_size, color, yaxis, rotate):
    if file:
        font = Fonts[font]
        color = Colors[color]
        transcriptFile(file, maxcap, font, font_size, color, yaxis, rotate)
    else:
        recordAudio()

# reads flags and arguments on command line. setsup argparse
def getArguments():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="generates subtitles for given mp4 file.\nIf file name is not specified, records audio live",
        epilog="9 + 10 != 21"
    )
    parser.add_argument('-f', '--file', type=str, help="Filename for generating subtitles")
    parser.add_argument('-m', '--maxcap', type=int, help="Maximum words per caption (default=4)")
    parser.add_argument('-F', '--font', type=str, help="Selectable font type (default='FONT_HERSHEY_SIMPLEX')")
    parser.add_argument('-S', '--font_size', type=float, help="Selectable font size (default=0.8) *font scale factor from their base size")
    parser.add_argument('-c', '--color', type=str, help="Text color bgr (default='green')")
    parser.add_argument('-y', '--yAxis', type=int, help="Where on the yaxis of the screen from top to bottom as a percentage (default=50)")
    parser.add_argument('-r', '--rotate', type=int, help="How many 90deg rotations counterclockwise. (e.g. 1 == 90, 3 == 270, default=0)")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArguments()
    file = args.file if args.file else None
    maxcap = args.maxcap if args.maxcap else 4
    font = args.font if args.font else 'simplex'
    font_size = args.font_size if args.font_size else 0.8
    color = args.color if args.color else 'green'
    yaxis = args.yAxis if args.yAxis else 50
    rotate = args.rotate if args.rotate else 0

    transcriptAudio(file, maxcap, font, font_size, color, yaxis, rotate)