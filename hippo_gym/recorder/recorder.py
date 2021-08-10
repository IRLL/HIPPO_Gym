import json
from os import makedirs, listdir
from shutil import rmtree
import _pickle as pickle


class Recorder:
    def __init__(self, hippo, path=None, mode=None, clean_path=False):
        self.mode = mode if mode else 'pickle'
        self.hippo = hippo
        self.path = path if path else 'Records'
        self.current_file = None

        if clean_path:
           try:
               rmtree(self.path)
               print('Removed:', self.path)
           except:
               pass
        makedirs(self.path, exist_ok=True)

    def record(self, data, filename=None):
        if self.mode == 'json':
            mode = 'a'
        else:
            mode = 'ab'
        if filename:
            outfile = open(f'{self.path}/{filename}', mode)
            self.write(data, outfile)
            outfile.close()
        elif self.current_file:
            self.write(data, self.current_file)
        else:
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
            try:
                self.current_file.close()
            except:
                pass
        self.current_file = open(f'{self.path}/{new_filename}', mode)
