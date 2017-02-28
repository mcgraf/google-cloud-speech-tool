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