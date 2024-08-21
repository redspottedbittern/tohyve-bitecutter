# Cutter of bite-sized pieces for the ToHyve Text to Speech conversion

This container functions as a small wrapper for the ToHyve TTS service to let it process larger text. Normally the TTS service sends an error message, if the input text is too long. The Bite Cutter takes the input text, sends it to the TTS and recursively cuts the text into smaller pieces, if an error arises.

**At the moment the container only works as a local machine and not yet over the web.**

## To interact with the tool:

- The interaction is basically the same as with the TTS tool itself with only a few differences

1. Create the audio file:
```bash
	curl -X POST \
      -H "Content-Type:application/json" \
      -d @curl.json \
      -o predict.txt \
      http://localhost:8006/split
```
Where curl.json is a JSON file, which contains input data.
```json
{
    "data": [
        "de",
        "Zum Frühstück gibt es Marmelade."
    ]
}
```
The file predict.txt is a text file, that will contain the path of the audio file after it was created.

2. Download the created audio file, using the path from the predict.txt file
```bash
curl -o /tmp/output.wav \
http://localhost:8006/app/$FILEPATH$
```
