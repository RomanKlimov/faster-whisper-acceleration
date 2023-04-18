import os
import re
import tempfile
from typing import List
import ffmpeg
import concurrent.futures
import time
from faster_whisper import WhisperModel
import multiprocessing


def find_optimal_breakpoints(points: List[float], n: int) -> List[float]:
    result = []
    optimal_length = points[-1] / n
    temp = 0
    temp_a = 0
    l = len(points)
    for i in points[:l - 1]:
        if (i - temp_a) >= optimal_length:
            if optimal_length - (temp - temp_a) < (i - temp_a) - optimal_length:
                result.append(temp)
            else:
                result.append(i)
            temp_a = result[-1]
        temp = i
    return result


def split_audio_into_chunks(input_file: str, max_chunks: int,
                            silence_threshold: str = "-20dB", silence_duration: float = 2.0) -> List[str]:
    def save_chunk_to_temp_file(input_file: str, start: float, end: float) -> str:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file.close()

        in_stream = ffmpeg.input(input_file)
        (
            ffmpeg.output(in_stream, temp_file.name, ss=start, t=end - start, c="copy")
            .overwrite_output()
            .run()
        )

        return temp_file.name

    def get_silence_starts(input_file: str) -> List[float]:
        silence_starts = [0.0]

        reader = (
            ffmpeg.input(input_file)
            .filter("silencedetect", n=silence_threshold, d=str(silence_duration))
            .output("pipe:", format="null")
            .run_async(pipe_stderr=True)
        )

        silence_end_re = re.compile(
            r" silence_end: (?P<end>[0-9]+(\.?[0-9]*)) \| silence_duration: (?P<dur>[0-9]+(\.?[0-9]*))"
        )

        while True:
            line = reader.stderr.readline().decode("utf-8")
            if not line:
                break

            match = silence_end_re.search(line)
            if match:
                silence_end = float(match.group("end"))
                silence_dur = float(match.group("dur"))
                silence_start = silence_end - silence_dur
                silence_starts.append(silence_start)

        return silence_starts

    file_extension = os.path.splitext(input_file)[1]
    metadata = ffmpeg.probe(input_file)
    duration = float(metadata["format"]["duration"])

    silence_starts = get_silence_starts(input_file)
    silence_starts.append(duration)

    temp_files = []
    current_chunk_start = 0.0

    n = max_chunks
    selected_items = find_optimal_breakpoints(silence_starts, n)
    selected_items.append(duration)

    for j in range(0, len(selected_items)):
        temp_file_path = save_chunk_to_temp_file(input_file, current_chunk_start, selected_items[j])
        temp_files.append(temp_file_path)

        current_chunk_start = selected_items[j]

    return temp_files


def transcribe_file(file_path, model):
    segments, info = model.transcribe(file_path)
    segments = list(segments)
    return segments


def transcribe_audio(input_file: str, max_processes = 0,
                     silence_threshold: str = "-20dB", silence_duration: float = 2.0, model=None) -> str:
    if max_processes > multiprocessing.cpu_count() or max_processes == 0:
        max_processes = multiprocessing.cpu_count()

    # Split the audio into chunks
    temp_files_array = split_audio_into_chunks(input_file, max_processes, silence_threshold, silence_duration)
    start = time.time()
    futures = []
    # Submit each file to the thread pool and store the corresponding future object
    with concurrent.futures.ThreadPoolExecutor(max_processes) as executor:
        for file_path in temp_files_array:
            future = executor.submit(transcribe_file, file_path, model)
            futures.append(future)

    result_string = ""
    for future in futures:
        segments = future.result()
        result_string += "".join(segment.text for segment in segments)

    end = time.time()
    print(end - start)

    # Remember to remove the temporary files after you're done processing them
    for temp_file in temp_files_array:
        os.remove(temp_file)
    return result_string


if __name__ == "__main__":
    # input audio file
    input_audio = "DonQuixote_OneHour.mp3"
    # number of processes to use
    max_processes = 8
    # load model
    model = WhisperModel("tiny", device="cpu", num_workers=max_processes, cpu_threads=2, compute_type="int8")
    result = transcribe_audio(input_audio, max_processes, silence_threshold="-20dB", silence_duration=2, model=model)
    print(result)
