import config
from __init__ import AudioToText


if '__main__' == __name__:
    import argparse
    args = argparse.ArgumentParser()
    args.add_argument('-c', '--config', dest='config_filename', required=True)
    args.add_argument('-a', '--audio-file', dest='audio_filename', required=True)
    args.add_argument('-q', '--quiet', dest='quiet', action='store_true')

    args.add_argument('--action-force', dest='force', action='store_true')
    args.add_argument('--action-compat', dest='convert_to_compat', action='store_true')
    args.add_argument('--action-upload', dest='upload_to_storage', action='store_true')
    args.add_argument('--action-text', dest='convert_to_text', action='store_true')

    args.add_argument('--sample-rate', dest='sample_rate', default=44100)
    args.add_argument('--sample-enc', dest='sample_encoding', default='FLAC')
    args.add_argument('--interval', dest='interval', default='')
    args.add_argument('--lang-code', dest='language_code', default=None)
    args.add_argument('--file-ext', dest='file_ext', default='.flac')
    args.add_argument('--async', dest='async', action='store_true')
    args.add_argument('--async-sleep', dest='async_sleep', type=int, default=5)
    args.add_argument('--async-retry', dest='async_retry', type=int, default=10)
    args.add_argument('--max-alts', dest='max_alts', type=int, default=2)

    args = args.parse_args()

    config = config.load(args.config_filename)
    a2t = AudioToText(config, args.audio_filename,
                      sample_rate=args.sample_rate,
                      sample_encoding=args.sample_encoding,
                      language_code=args.language_code,
                      interval=args.interval,
                      file_ext=args.file_ext,
                      async=args.async,
                      async_sleep=args.async_sleep,
                      async_retry=args.async_retry,
                      debug=not args.quiet)
    if args.force:
        a2t.delete_compat_file()
        a2t.delete_remote_blob()

    if args.convert_to_compat:
        a2t.convert_to_compat()

    if args.upload_to_storage:
        a2t.upload_to_storage()

    if args.convert_to_text:
        a2t.convert_to_text()
