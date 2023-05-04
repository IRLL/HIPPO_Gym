import json
import pickle
import os
from io import FileIO
from pathlib import Path
from typing import Optional

from abc import abstractmethod


class Recorder:
    def __init__(self, records_path="records", experiment_name: Optional[str] = None):
        self.path = Path(records_path)
        os.makedirs(self.path, exist_ok=True)
        self.current_file = None
        self.experiment_name = experiment_name if experiment_name else "exp"

    @abstractmethod
    def write(self, data, outfile: FileIO):
        """Write the data in the current file."""

    @abstractmethod
    def create_file(self, filepath: Path) -> FileIO:
        """Create a new file to record into."""

    def _create(self, filename: str):
        filepath = self.path / filename
        if self.current_file:
            self.close_file()
        self.current_file = self.create_file(filepath)

    def record(self, data, user_id: str):
        record_name = f"{self.experiment_name}_{user_id}"
        if not self.current_file:
            self._create(record_name)
        self.write(data, self.current_file)

    def close_file(self) -> None:
        if self.current_file:
            self.current_file.close()
            self.current_file = None


class JsonRecorder(Recorder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_record_written = False

    def write(self, data, outfile: FileIO):
        if self.first_record_written:
            outfile.write(",\n")
        else:
            self.first_record_written = True
        outfile.write(json.dumps(data))

    def close_file(self) -> None:
        if self.current_file:
            self.current_file.write("\n]")
            self.current_file.close()
            self.current_file = None
            self.first_record_written = False
    def create_file(self, filepath: Path) -> FileIO:
        """Create a new json to record into."""
        file = open(filepath.with_suffix(".json"), "w")
        file.write("[\n")
        return file
    def __del__(self):
        self.close_file()


class PickleRecorder(Recorder):
    def write(self, data, outfile: FileIO):
        pickle.dump(data, outfile)

    def create_file(self, filepath: Path) -> FileIO:
        """Create a new pickle file to record into."""
        return open(filepath.with_suffix(".pkl"), "wb")
