from __future__ import annotations

import os
from typing import TYPE_CHECKING

import _pickle as cPickle

if TYPE_CHECKING:
    from App.trial import Trial

class Recorder():

    def __init__(self, trial:Trial) -> None:
        self.trial = trial

        # File data
        self.outfile = None
        self.filename = None
        self.path = None

        self.record = []
        self.nextEntry = {}

    def reset(self) -> None:
        if self.outfile:
            self.outfile.close()
            if self.trial.config.get('s3upload'):
                self.trial.pipe.send({
                    'upload': {'projectId':self.trial.projectId, 'userId':self.trial.userId,
                        'file':self.filename, 'path':self.path,
                        'bucket': self.trial.config.get('bucket')}
                })
        self.create_file()

    def close(self) -> None:
        if self.trial.config.get('dataFile') == 'trial':
            self.save_record()
        if self.outfile:
            self.outfile.close()
            self.trial.pipe.send({
                'upload':{'projectId':self.trial.projectId,'userId':self.trial.userId,
                    'file':self.filename,'path':self.path}})

    def record_message(self, message:dict) -> None:
        self.update_entry(message)

    def record_render(self, render:dict) -> None:
        pass

    def record_step(self, env_state:dict) -> None:
        self.update_entry(env_state)

    def update_entry(self, update_dict:dict) -> None:
        '''
        Adds a generic dictionary to the self.nextEntry dictionary.
        '''
        self.nextEntry.update(update_dict)

    def save_entry(self) -> None:
        '''
        Either saves step memory to self.record list or pickles the memory and
        writes it to file, or both.
        Note that observation and render objects can get large, an episode can
        have several thousand steps, holding all the steps for an episode in 
        memory can cause performance issues if the os needs to grow the heap.
        The program can also crash if the Server runs out of memory. 
        It is recommended to write each step to file and not maintain it in
        memory if the full observation is being saved.
        comment/uncomment the below lines as desired.
        '''
        if self.config.get('dataFile') == 'trial':
            self.record.append(self.nextEntry)
        else:
            cPickle.dump(self.nextEntry, self.outfile)
            self.nextEntry = {}

    def save_record(self) -> None:
        '''
        Saves the self.record object to file. Is only called if uncommented in
        self.end(). To record full trial records a line must also be uncommented
        in self.save_entry() and self.create_file()
        '''
        cPickle.dump(self.record, self.outfile)
        self.record = []

    def create_file(self) -> None:
        '''
        Creates a file to record records to. comment/uncomment as desired 
        for episode or full-trial logging.
        '''
        if self.trial.config.get('dataFile') == 'trial':
            filename = f'trial_{self.trial.userId}'
        else:
            filename = f'episode_{self.trial.episode}_user_{self.trial.userId}'
        path = os.path.join('Trials', filename)
        if not os.path.exists('Trials'):
            os.makedirs('Trials')
        self.outfile = open(path, 'ab')
        self.filename = filename
        self.path = path
