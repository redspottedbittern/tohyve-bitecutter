"""Util functions for the bite cutter docker."""

import os
import requests
from nltk.tokenize import sent_tokenize, word_tokenize
from pydub import AudioSegment


async def process_loop(tts_url, text, language):
    """Sends input text recursively to TTS and splits it if needed.

    Returns a list of filepaths to the soundfiles."""

    # make a http request to the TTS model
    output = requests.post(tts_url, json={"data": [language, text]})
    output = output.json()

    # base case: text can be processed
    if was_processed(output):
        return [extract_filepath(output)]

    # use the custom split method
    bites = split(text)

    # start the recursion for all text bites
    filepaths = []
    for bite in bites:
        filepaths.extend(await process_loop(tts_url, bite, language))

    return filepaths


def was_processed(output):
    """Checks if the TTS service could handle the text input.

    The TTS service output is a hash map either containing the key 'data' if
    processing was successful or containing the key 'error' if unsuccessful.
    """

    if 'data' in output.keys():
        return True
    elif 'error' in output.keys():
        return False
    else:
        raise AssertionError


def extract_filepath(output):
    return output['data'][0]['name']


def split(text):
    """Splits text into sentences or sentences into half the number of
    words."""

    # split into sentences and return if there are more than one
    sentences = sent_tokenize(text)

    if len(sentences) > 1:
        return sentences

    # split into words and join everything to the mid point
    words = word_tokenize(text)

    mid = len(words) // 2
    words_first_half = ' '.join(words[:mid])
    words_second_half = ' '.join(words[mid:])

    return [words_first_half, words_second_half]


async def download_wav(file_url, download_dir, filepaths):
    """Downloads files from TTS service and returns filepaths."""

    local_filepaths = []
    local_file = "_downloaded.wav"

    for idx, path in enumerate(filepaths):

        # set the full remote and local paths
        full_remote_path = file_url + path
        full_local_path = download_dir + str(idx) + local_file

        # send a http GET to download from the TTS service
        file_response = requests.get(full_remote_path)

        # save the file to the local folder
        with open(full_local_path, 'wb') as file:
            file.write(file_response.content)

        local_filepaths.append(full_local_path)

    return local_filepaths


async def concatenate_wav(filepaths, output_path):
    """Use AudioSegment to concatenate the wav files."""

    # initialize Audiosegment and concatenate the wav files onto it
    big_wav = AudioSegment.empty()

    for wav in filepaths:
        # Check if file already exists
        if os.path.exists(wav):
            big_wav += AudioSegment.from_wav(wav)
        else:
            raise FileNotFoundError

    # Save the output file
    big_wav.export(output_path, format='wav')


def delete_wav(filepaths):
    """Deletes temporary wav bites."""

    for wav in filepaths:
        if os.path.exists(wav):
            os.remove(wav)
