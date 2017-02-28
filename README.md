# Google Cloud Speech Tool

This is a quick hack script made in a few days, but I hope to use it as a guide in building other
tools that work with the Google Cloud Speech API.

## Getting started

Install the dependencies. **Note that this script uses `ffmpy` which requires `ffmpeg` to be
installed on the system.**

```bash
pip install -r requirements.txt
```

The configuration file encapsulates a few options used by the script.

| Name | Description |
| --- | --- |
| _google_cloud (dict)_ | GC specific settings
| _google_cloud.credentials_file (str)_ | simple path to a GC project credentials file
| _google_cloud.storage (dict)_ | details related to GC Storage
| _google_cloud.storage.bucket (str)_ | bucket name where to store files in case you want to upload audio files and analyze them from GCS
| _google_cloud.storage.remote_dir (str)_ | sub directory within the bucket where the script can freely upload/destroy files


The script `a2t.py` provides four main actions:

* `--action-upload`: uploads an audio file to GCS
* `--action-force`: if the current audio file (`-a`) has been previously converted and exists on 
the FS or in GCS, destroy both of them
* `--action-compat`: runs an `ffmpeg` command to convert the input file (`-a`) into a single 
channel with the format set in `--file-ext`
* `--action-text`: submits the compatible audio file created by `--action-compat` to the speech 
recognition API
 
The remainder of the options apply to the speech recognition API:

* `--sample-rate`: indicates the sample rate of the input file
* `--sample-enc`: indicates the sample encoding (recommend `--async --sample-enc LINEAR16`, 
`--sample-enc FLAC # without --async`) (see `google.cloud.speech.Encoding.*` for valid all values)
* `--file-ext`: indicates the file extension of the desired format for upload
(recommend `--async --file-ext .wav`, `--file-ext .flac # without --async`)
* `--async`: calls the `async_recognize` Speech API function; calls `sync_recognize` if this is 
not present
* `--async-retry`: indicates the number of times to call and check for the result of an 
`async_recognize` operation
* `--async-sleep`: indicates the number of seconds to wait in between checks of an 
`async_recognize` operation
* `--max-alts`: indicates the number of alternatives that will be returned from the Speech API
* `--interval`: this extracts an interval of the input audio file for conversion to text 
(i.e. `5,10` indicates from `5s` to `10s`)
* `--lang-code`: this indicates the language code to pass to the Speech API as a hint

## Usage

```
usage: a2t.py [-h] -c CONFIG_FILENAME -a AUDIO_FILENAME [-q] [--action-force]
              [--action-compat] [--action-upload] [--action-text]
              [--sample-rate SAMPLE_RATE] [--sample-enc SAMPLE_ENCODING]
              [--interval INTERVAL] [--lang-code LANGUAGE_CODE]
              [--file-ext FILE_EXT] [--async] [--async-sleep ASYNC_SLEEP]
              [--async-retry ASYNC_RETRY] [--max-alts MAX_ALTS]
```

## Example

```bash
#!/bin/bash
#
# This example illustrates a working set of options for the async recognition method
#
FILENAME=$1
[[ -z "$FILENAME" || ! -f "$FILENAME" ]] && echo "audio file not found" && exit 1

python gcs_tool/a2t.py -c config.yml -a "$FILENAME" \
  --interval 0,59 \
  --sample-enc LINEAR16 \
  --file-ext .wav \
  --async --async-sleep 2 --async-retry 150 \
  --max-alts 1 \
  --lang-code en-GB \
  --action-compat \
  --action-upload \
  --action-text \
  --action-force
```