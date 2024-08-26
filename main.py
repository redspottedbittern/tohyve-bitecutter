from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from utils import process_loop, download_wav, concatenate_wav, delete_wav

# Set url for the TTS service
# SERVER_URL = "https://dfki-3109.dfki.de/"
# SERVER_URL = "http://localhost:8003/"
SERVER_URL = "http://tts_container:8003/"
TTS_URL = SERVER_URL + "tts/run/predict"
FILE_URL = SERVER_URL + "tts/file="

# Set path of temporary download folder and for the save file
DOWNLOAD_DIR = "/app/downloads/"
OUTPUT_PATH = '/app/output.wav'

# define the fastapi app
app = FastAPI()


# use pydantics BaseModel to validate the incoming POST requests
class TextInput(BaseModel):
    data: List[str]


@app.post("/split")
async def request_handler(input: TextInput):
    """Uses the TTS service to turn text into speech.

    process_loop: recursively send text to the TTS service and splits it into
    smaller chunks if the service can't handle the size.

    download_wav, concatenate_wav, delete_wav: deal with a number of generated
    wav files to expose them for http requests
    """

    # extract the field from the TextInput class and
    # get the filepaths by sending text to the TTS
    language = input.data[0]
    text = input.data[1]
    filepaths = await process_loop(TTS_URL, text, language)

    # download all the small wav files
    local_filepaths = await download_wav(FILE_URL, DOWNLOAD_DIR, filepaths)

    # Concatenate the small files into a big one
    await concatenate_wav(local_filepaths, OUTPUT_PATH)

    # clean up by deleting wav bites
    delete_wav(local_filepaths)

    return OUTPUT_PATH


@app.get(OUTPUT_PATH)
def get_file():
    """Returns the output file for a http GET comand."""
    return FileResponse(OUTPUT_PATH, media_type="audio/wav")
