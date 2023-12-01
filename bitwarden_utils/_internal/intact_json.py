import json
import hashlib
import os

class JsonChecksumHandler:
    def __init__(self, filepath : str, defaultData = {}):
        if not filepath.endswith(".json"):
            self.json_file_path = f"{filepath}.json"
            self.checksum_file_path = f"{filepath}.checksum"
        else:
            self.json_file_path = filepath
            self.checksum_file_path = os.path.splitext(filepath)[0] + ".checksum"

        if not os.path.exists(self.json_file_path):
            self.update_json(defaultData)

        if not os.path.exists(self.checksum_file_path):
            raise FileNotFoundError(f"{self.checksum_file_path} does not exist")
        
        self.__cache = None

    def read_json(self):
        if self.__cache:
            return self.__cache

        with open(self.json_file_path, 'r') as file:
            data= json.load(file)
            self.__cache = data

        return data


    def calculate_checksum(self):
        with open(self.json_file_path, 'rb') as file:
            file_content = file.read()
            return hashlib.sha256(file_content).hexdigest()

    def read_checksum_file(self):
        with open(self.checksum_file_path, 'r') as file:
            return file.read().strip()

    def verify_checksum(self):
        calculated_checksum = self.calculate_checksum()
        file_checksum = self.read_checksum_file()
        return calculated_checksum == file_checksum

    def update_json(self, data):
        self.__cache = None

        with open(self.json_file_path, 'w') as file:
            json.dump(data, file)
        self.update_checksum_file()

    def update_checksum_file(self):
        checksum = self.calculate_checksum()
        with open(self.checksum_file_path, 'w') as file:
            file.write(checksum)
