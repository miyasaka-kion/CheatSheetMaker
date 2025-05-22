import os
from openai import OpenAI
from pathlib import Path
import tiktoken
import json
import sys
from tqdm import tqdm

class ChunkProcessor:
    def __init__(self, 
                 model, 
                 chunk_size, 
                 api_key, 
                 base_url,
                 timeout):
        if not all([model, chunk_size, api_key]):
            raise ValueError("Missing one or more required values: model, chunk_size, api_key, prompt_file")
        self.model = model
        self.chunk_size = chunk_size
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )
        self.prompt : str = None

    def _count_tokens(self, text):
        try:
            enc = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Fallback to a default encoding, e.g., cl100k_base
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

    def _split(self, input):
        lines = input.split("\n")
        chunks = []
        current_chunk = ""
        token_count = 0
        i = 0
        while i < len(lines):
            line = lines[i]
            line_tokens = self._count_tokens(line + "\n")
            if token_count + line_tokens > self.chunk_size:
                # read until the next blank line
                while i < len(lines) and lines[i].strip() != "":
                    current_chunk += lines[i] + "\n"
                    i += 1
                while i < len(lines) and lines[i].strip() == "":
                    current_chunk += lines[i] + "\n"
                    i += 1
                chunks.append(current_chunk)
                current_chunk = ""
                token_count = 0
            else:
                current_chunk += line + "\n"
                token_count += line_tokens
                i += 1
        if current_chunk.strip():
            chunks.append(current_chunk)
        return chunks

    def _process_chunk(self, chunk):
        prompt_with_chunk = self.prompt.format(chunk=chunk)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt_with_chunk}],
            temperature=0.3
        )

        if hasattr(response.choices[0].message, 'reasoning_content'):
            print(response.choices[0].message.reasoning_content)
        return response.choices[0].message.content

        
    def process(self, input: str, prompt: str) -> str:
        chunks = self._split(input)
        processed = []
        self.prompt = prompt
        
        for i, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
            processed.append(self._process_chunk(chunk))
        return "\n".join(processed)
