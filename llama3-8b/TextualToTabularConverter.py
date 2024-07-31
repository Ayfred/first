"""
import csv
import re
import configparser

class TextualToTabularConverter:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        self.input_file = self.config['llama-3-8b']['input_file']
        self.output_file = self.config['llama-3-8b']['output_file']
        self.data = ""
        self.matches = []
        data_in_use = self.config['dataset']['data_in_use']
        self.headers = self.config[data_in_use]['headers'].split(', ')
        self.pattern = re.compile(self.config['llama-3-8b']['pattern'], re.MULTILINE)

    def read_data(self):
        print("Reading data from:", self.input_file)
        with open(self.input_file, 'r') as file:
            self.data = file.read()

    def parse_data(self):
        print("Parsing data...")
        # Remove any unwanted text
        self.data = re.sub(r'HAEMATOCRIT: \d+\.\d+"', '', self.data)
        
        # Extract individual patient data blocks
        patient_blocks = re.split(r'\nPatient \d+:\n', self.data)
        for block in patient_blocks:
            block = block.strip()
            if block:
                # Extract the values using the headers
                match = [self.extract_value(block, header) for header in self.headers]
                self.matches.append(match)

    def extract_value(self, block, header):
        # Use regex to extract the value corresponding to the header
        pattern = re.compile(rf'{header}:\s*([^,\n]+)')
        match = pattern.search(block)
        if match:
            return match.group(1).strip()
        return ""

    def write_csv(self):
        print("Writing CSV to:", self.output_file)
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)
            for match in self.matches:
                # Handle potential trailing backslash
                cleaned_match = [value.rstrip('\\') for value in match]
                writer.writerow(cleaned_match)

    def process(self):
        print("Starting data processing...")
        self.read_data()
        self.parse_data()
        self.write_csv()
        print("Data processing complete.")
"""

import csv
import re
import configparser

class TextualToTabularConverter:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        self.input_file = self.config['llama-3-8b']['input_file']
        self.output_file = self.config['llama-3-8b']['output_file']
        self.data = ""
        self.matches = []
        self.headers = ['Disease', 'Fever', 'Cough', 'Fatigue', 'Difficulty Breathing', 'Age', 'Gender', 'Blood Pressure', 'Cholesterol Level', 'Outcome Variable']
        self.pattern = re.compile(
            r'Patient \d+: \[Disease: (.*?), Fever: (.*?), Cough: (.*?), Fatigue: (.*?), Difficulty Breathing: (.*?), Age: (\d+), Gender: (.*?), Blood Pressure: (.*?), Cholesterol Level: (.*?), Outcome Variable: (.*?)\]'
        )

    def read_data(self):
        print("Reading data from:", self.input_file)
        with open(self.input_file, 'r') as file:
            self.data = file.read()

    def parse_data(self):
        print("Parsing data...")
        self.matches = self.pattern.findall(self.data)

    def write_csv(self):
        print("Writing CSV to:", self.output_file)
        with open(self.output_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.headers)
            for match in self.matches:
                writer.writerow(match)

    def process(self):
        print("Starting data processing...")
        self.read_data()
        self.parse_data()
        self.write_csv()
        print("Data processing complete.")