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
from video_transcriber import VideoTranscriber

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
def transcriptFile(file, maxcap):
    try:
        if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):  # Video files
            transcriber = VideoTranscriber(file, maxcap)
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
def transcriptAudio(file, maxcap=4):
    if file:
        transcriptFile(file, maxcap)
    else:
        recordAudio()

# reads flags and arguments on command line. setsup argparse
def getArguments():
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="generates subtitles for given mp4 file.\nIf file name is not specified, records audio live",
        epilog="9 + 10 != 21"
    )
    parser.add_argument('-f', '--file', type=str, help="Filename for generating subtitles (optional)")
    parser.add_argument('-m', '--maxcap', type=int, help="Maximum Characters per caption (default=4)")
    return parser.parse_args()

if __name__ == "__main__":
    args = getArguments()
    file = args.file
    maxcap = args.maxcap
    transcriptAudio(file, maxcap)