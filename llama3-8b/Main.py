# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed in accordance with the terms of the Llama 3 Community License Agreement.

from typing import List, Optional
import fire
import sys
import TabularToTextualConverter as TabularToTextualConverter
import TextualToTabularConverter as TextualToTabularConverter
import os
import configparser

sys.path.append("./llama3")
from llama import Dialog, Llama


CONFIG_FILE = "../config.ini"

def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0.6,
    top_p: float = 0.9,
    max_seq_len: int = 512,
    max_batch_size: int = 4,
    max_gen_len: Optional[int] = None,
):
    """
    Examples to run with the models finetuned for chat. Prompts correspond of chat
    turns between the user and assistant with the final one always being the user.

    An optional system prompt at the beginning to control how the model should respond
    is also supported.

    The context window of llama3 models is 8192 tokens, so `max_seq_len` needs to be <= 8192.

    `max_gen_len` is optional because finetuned models are able to stop generations naturally.
    """

    print("Reading configuration file...")
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    dataset = config['dataset']['data_in_use']
    data = config[dataset]['data_dir']

    print("Formatting patient data...")
    patient_data_formatter = TabularToTextualConverter.TabularToTextualConverter(data)
    patient_data_formatter.read_data()
    patient_data_formatter.transform_rows()
    #combined_string = patient_data_formatter.get_combined_string()

    subset_data = patient_data_formatter.get_subset_data(number_of_patients=11)

    print("Building Llama generator...")
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    i = 0

    input_text = config['llama-3-8b']['input_text']

    while i < len(subset_data):
        print("Generating patient records... number: " + str(i))
        dialogs: List[Dialog] = [
            [{"role": "user", "content": input_text +  str(subset_data[i])}],
        ]

        results = generator.chat_completion(
            dialogs,
            max_gen_len=max_gen_len,
            temperature=temperature,
            top_p=top_p,
        )

        print("Printing generated records...")
        
        results_txt = config['llama-3-8b']['input_file']

        # Check if the file exists
        if not os.path.exists(results_txt):
            # Create the file if it doesn't exist
            with open(results_txt, 'w') as f:
                pass

        # Store the results in a txt file
        print("Storing the results in txt file...")
        lines_to_skip = ["User:", "Use", "Data:", "> Assistant:", "Note:", "Patient i:", "Note that", "Let me", "And put the data"]

        def filter_lines(text: str, prefixes: List[str]) -> str:
            filtered_lines = []
            for line in text.splitlines():
                if not any(line.startswith(prefix) for prefix in prefixes):
                    filtered_lines.append(line)
            return "\n".join(filtered_lines)

        with open(results_txt, 'a') as f:
            for dialog, result in zip(dialogs, results):
                dialog_content = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in dialog])
                result_content = f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
                combined_content = dialog_content + "\n" + result_content
                
                filtered_content = filter_lines(combined_content, lines_to_skip)
                
                f.write(filtered_content + "\n\n")

        i += 1
        


    print("Converting generated text to tabular format...")
    converter = TextualToTabularConverter.TextualToTabularConverter(CONFIG_FILE)
    converter.process()

if __name__ == "__main__":
    fire.Fire(main)
