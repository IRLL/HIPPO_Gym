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
        self.current_file = None

    def write(self, data, filepath: Path):
        print("Writing data to file:", data)
        with open(filepath, "r") as file:
            content = file.read()
            if content[-2:] == "\n]":
                content = content[:-2] + ",\n"
            else:
                content = content[:-1]  # Remove the last "]" character
                content += "\n"  # Add newline character
            content += json.dumps(data) + "\n]"
        with open(filepath, "w") as file:
            file.write(content)


    def close_file(self) -> None:
        print("Closing file")
        if self.current_file:
            self.current_file.write("\n]")
            self.current_file.flush()
            self.current_file.close()
            self.current_file = None
            self.first_record_written = False
    def create_file(self, filepath: Path) -> FileIO:
        """Create a new json to record into."""
        print(f"Creating file at: {filepath.with_suffix('.json')}")
        if not os.path.exists(filepath.with_suffix(".json")):
            file = open(filepath.with_suffix(".json"), "w")
            file.write("[\n")
            file.close()
        return filepath.with_suffix(".json")

    def __del__(self):
        self.close_file()


class PickleRecorder(Recorder):
    def write(self, data, outfile: FileIO):
        pickle.dump(data, outfile)

    def create_file(self, filepath: Path) -> FileIO:
        """Create a new pickle file to record into."""
        return open(filepath.with_suffix(".pkl"), "wb")
