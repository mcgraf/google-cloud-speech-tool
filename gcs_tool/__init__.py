from __future__ import print_function
from subprocess import PIPE
from ffmpy import FFmpeg
from google.cloud import speech
import io
import os
import time
import config


class AudioToText(object):
    def __init__(self, _config, filename,
                 sample_rate=44100,
                 language_code=None,
                 interval='',
                 file_ext='.flac',
                 sample_encoding=speech.Encoding.LINEAR16,
                 async=False,
                 async_sleep=5,
                 async_retry=10,
                 max_alternatives=2,
                 debug=True):
        """

        Args:
            _config (config.Config):
            filename (str):
        """
        self.debug = debug
        self._async = async
        self._async_sleep = async_sleep
        self._async_retry = async_retry
        self.file_ext = file_ext
        self.max_alternatives = max_alternatives
        self.interval = interval.split(',') if ',' in interval else []
        self.sample_encoding = sample_encoding
        self.sample_rate = sample_rate
        self.language_code = language_code
        self.config = _config
        self.audio_filename = self.config.get_resource_path(filename)
        if not os.path.isfile(self.audio_filename):
            raise Exception('File not found: {0}'.format(self.audio_filename))
        bn = os.path.basename(self.audio_filename)
        name, ext = os.path.splitext(bn)
        self.compat_filename = os.path.join('/tmp', ''.join([name, self.file_ext]))

    def log(self, *args):
        if self.debug:
            print(' '.join([str(arg) for arg in args]))

    def get_remote_name(self):
        return '/'.join([
            self.config.google_cloud['storage']['remote_dir'],
            os.path.basename(self.compat_filename.replace(' ', '_'))
        ])

    def get_remote_blob(self):
        buck = self.config.get_bucket()
        return buck.blob(self.get_remote_name())

    def is_uploaded(self):
        return self.get_remote_blob().exists()

    def delete_remote_blob(self):
        if self.is_uploaded():
            return self.get_remote_blob().delete()

    def delete_compat_file(self):
        if os.path.isfile(self.compat_filename) and self.compat_filename != self.audio_filename:
            os.unlink(self.compat_filename)

    def convert_to_compat(self):
        self.log('convert to', self.file_ext, self.audio_filename, '>', self.compat_filename)
        if not os.path.isfile(self.compat_filename):
            inopts = []
            if self.interval:
                inopts.extend([
                    '-ss', self.interval[0],
                    '-t', self.interval[1],
                ])
            ff = FFmpeg(
                inputs={self.audio_filename: inopts},
                outputs={self.compat_filename: [
                    '-ar', str(self.sample_rate),
                    '-ac', '1',
                ]}
            )
            self.log('converting using', ff.cmd)
            self.log(ff.cmd)
            ff.run(stderr=PIPE, stdout=PIPE)
        self.log('converted to', self.file_ext)

    def upload_to_storage(self):
        self.log('upload blob', self.get_remote_name(), self.is_uploaded())
        blob = self.get_remote_blob()
        if not self.is_uploaded():
            self.log('uploading...')
            blob.upload_from_filename(self.compat_filename)
        self.log('uploaded blob')
        return blob

    def convert_to_text(self):
        if not self.is_uploaded():
            fn = self.audio_filename
            if os.path.isfile(self.compat_filename):
                fn = self.compat_filename
            self.log('converting to text', fn)
            with io.open(fn, 'rb') as f:
                source_uri = None
                content = f.read()
        else:
            source_uri = self.config.get_bucket_source_uri(self.get_remote_name())
            content = None

        sample = self.config.get_speech().sample(
            content=content,
            source_uri=source_uri,
            encoding=self.sample_encoding,
            sample_rate=self.sample_rate,
        )

        if self._async:
            operation = sample.async_recognize(
                max_alternatives=self.max_alternatives,
                language_code=self.language_code,
            )
            retry_count = self._async_retry
            timeout = self._async_sleep
            while retry_count > 0 and not operation.complete:
                retry_count -= 1
                operation.poll()
                if not operation.complete:
                    self.log('waiting for', timeout, 's', '({0})'.format(retry_count))
                    time.sleep(timeout)
            results = operation.results
        else:
            results = sample.sync_recognize(
                max_alternatives=self.max_alternatives,
                language_code=self.language_code,
            )

        for result in results:
            for alt in result.alternatives:
                print('=' * 20)
                print(alt.transcript)
                print(alt.confidence)
