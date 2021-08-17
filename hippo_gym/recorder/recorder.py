import json
from os import makedirs, listdir
from shutil import rmtree
import _pickle as pickle

from hippo_gym.recorder.uploader import Uploader


class Recorder:
    def __init__(self, hippo, path=None, mode=None, clean_path=False, upload=False):
        self.mode = mode if mode else 'pickle'
        self.hippo = hippo
        self.path = path if path else 'Records'
        self.current_file = None
        self.current_filename = None
        self.uploader = Uploader() if upload else None

        if clean_path:
           try:
               rmtree(self.path)
               print('Removed:', self.path)
           except:
               pass
        makedirs(self.path, exist_ok=True)

    def record(self, data):
        if not self.current_file:
            self.create_file()
        self.write(data, self.current_file)

    def write(self, data, outfile):
        if self.mode == 'json':
            outfile.write(json.dumps(data))
            outfile.write('\n')
        else:
            pickle.dump(data, outfile)

    def create_file(self, filename=None):
        if self.mode == 'json':
            ext = 'json'
            mode = 'w'
        else:
            ext = 'pk'
            mode = 'wb'
        if not filename:
            filename = f'user_{self.hippo.user_id}.{ext}'
        ls = listdir(self.path)
        i = 0
        new_filename = f'{i}_{filename}'
        while new_filename in ls:
            i += 1
            new_filename = f'{i}_{filename}'
        if self.current_file:
            self.close_file()
        self.current_file = open(f'{self.path}/{new_filename}', mode)
        self.current_filename = new_filename

    def close_file(self):
        if self.current_file:
            self.current_file.close()
            self.current_file = None
            self.upload(self.current_filename)
            self.current_filename = None

    def upload(self, file=None):
        if self.uploader:
            filename = file if file else self.current_filename
            if filename == self.current_filename:
                if self.current_file:
                    self.current_file.close()
                    self.uploader.run(self.path, filename)
                    if self.mode == 'json':
                        mode = 'a'
                    else:
                        mode = 'ab'
                    self.current_file = open(f'{self.path}/{self.current_filename}', mode)
            self.uploader.run(self.path, filename)
