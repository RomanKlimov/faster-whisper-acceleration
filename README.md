<!-- ABOUT THE PROJECT -->
## About The Project


This program dramatically accelerates the transcribing of single audio files using Faster-Whisper by splitting the file into smaller chunks at moments of silence, ensuring no loss in transcribing quality. By consuming and processing each audio chunk in parallel, this project achieves significant acceleration using only CPUs.

Why?

faster-whisper has no option to automatically split the file and parallelize the execution.
This project is a wrapper for faster-whisper that allows you to speed up transcribing of big single audio files.

Here is the discussion about this issue:
https://github.com/guillaumekln/faster-whisper/issues/133


## Features
 - Utilizes Faster-Whisper for efficient and accurate audio transcribing.
 - Splits the input audio file into optimal size chunks based on the number of available processes.
 - Automatically detects moments of silence using ffmpeg to split the audio without affecting transcribing quality.
 - Supports parallel processing using multiple CPU cores to speed up transcribing.

## Installation
Before you begin, ensure you have the following dependencies installed:

 - Python 3.6 or higher
 - ffmpeg
 - faster_whisper

## Usage
 - Import the necessary functions from the script:
```Python
from parallelization import transcribe_audio
```
 - Load the Faster-Whisper model with your desired settings:
```Python
from faster_whisper import WhisperModel
model = WhisperModel("tiny", device="cpu", num_workers=max_processes, cpu_threads=2, compute_type="int8")
```
 - Call the transcribe_audio function with the desired input file, the number of processes (up to the number of available CPU cores), and optional silence threshold and duration parameters:
```Python
input_audio = "your_audio_file.mp3"
max_processes = 4  # Adjust this value based on the available CPU cores
result = transcribe_audio(input_audio, max_processes, silence_threshold="-20dB", silence_duration=2, model=model)
```
 - The result variable will contain the transcribed text.

## Example
Here's an example of how to use the program:
```Python
from parallelization import transcribe_audio
from faster_whisper import WhisperModel

if __name__ == "__main__":
    # input audio file
    input_audio = "DonQuixote_OneHour.mp3"
    # number of processes to use
    max_processes = 4
    # load model
    model = WhisperModel("tiny", device="cpu", num_workers=max_processes, cpu_threads=2, compute_type="int8")
    result = transcribe_audio(input_audio, max_processes, silence_threshold="-20dB", silence_duration=2, model=model)
    print(result)
```

## Performance Testing
All testing was done on a MacBook M1 Pro CPU, 8 cores, with 16G of RAM.


The input file duration was 3706.393 seconds - 01:01:46(H:M:S)  

| Processes | Model | Completed     | Speed               |
|----| ----- |---------------|---------------------|
| 001|  tiny | 121.3 seconds | 30.56x (foundation) |
| 002|  tiny | 87.7 seconds  | 42.26x              |
| 003|  tiny | 60.9 seconds  | 60.86x              |
| 004|  tiny | 56.2 seconds  | 65.95x              |
| 005|  tiny | 61.1 seconds  | 60.66x              |
| 006|  tiny | 64.9 seconds  | 57.1x               |
| 007|  tiny | 65.93 seconds | 56.2x               |
| 008|  tiny | 62 seconds    | 59.78x              |


## License
This project is open source and available under the MIT License.