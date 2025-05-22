import os
import sys
import json
import shutil

from ChunkProcessor import ChunkProcessor
from FileHandler import FileHandler

from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
from marker.models import create_model_dict
from marker.output import text_from_rendered



class Generator:
    def __init__(self, config_path="config.json"):
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            config = {}

        self.processor = ChunkProcessor(
            model=config.get("model", "deepseek-v3-250324"),
            chunk_size=config.get("chunk_size", 4000),
            api_key=config.get("api_key", os.environ.get("ARK_API_KEY")),
            base_url=config.get("base_url", "https://ark.cn-beijing.volces.com/api/v3"),
            timeout=config.get("timeout", 1800)
        )
        self.input_dir = config.get("input_dir", "input")
        self.output_dir = config.get("output_dir", "output")
        self.base_name = config.get("base_name", os.path.basename(sys.argv[0]))

        self.input_file: FileHandler = None
        self.raw_md: FileHandler = None
        self.formatted_md: FileHandler = None
        self.cheatsheet_tex: FileHandler = None
        self.cheatsheet_pdf: FileHandler = None

    #     self.handlers: list = []

    # async def _run_handlers(self):
    #     tasks = [handler() for handler in self.handlers if asyncio.iscoroutinefunction(handler)]
    #     if tasks:
    #         await asyncio.gather(*tasks)

    # if current file is the entrance point, parse args
    def parse_args(self):
        if len(sys.argv) < 2:
            print("Usage: python main.py <input_file> ")
            exit(1)

        self.input_file = FileHandler(sys.argv[1])
        base = self.input_file.base

        self.raw_md = FileHandler(f"{self.input_dir}/{base}-raw.md")
        self.formatted_md = FileHandler(f"{self.input_dir}/{base}-formatted.md")
        self.cheatsheet_tex = FileHandler(f"{self.input_dir}/{base}-cheatsheet.tex")
        self.cheatsheet_pdf = FileHandler(f"{self.output_dir}/{base}-cheatsheet.pdf")
        self.generate_cheatsheet()

    def generate_cheatsheet(self):
        self._process_pdf_to_raw()
        self._process_raw_to_formatted()
        self._process_formatted_to_tex()
        self._render_tex()

    # stage 1: using marker to converty pdf to raw markdown
    # <filename>.pdf -> <filename-raw>.md
    def _process_pdf_to_raw(self):
        if self.raw_md.exists:
            print(f"File {self.raw_md.filename} already exists. Skipping PDF to raw markdown conversion.")
            return

        print(f"Stage 0: Processing PDF file: {self.input_file.filename} to {self.raw_md.filename}")
        marker_config = {
            "output_format": "markdown",
            "languages": "en",
            "output_dir": self.input_dir,
            "disable_image_extraction": True,
        }
        config_parser = ConfigParser(marker_config)
        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service()
        )
        rendered = converter(str(self.input_file.path))
        self.raw_md.buffer, _, _ = text_from_rendered(rendered)
        self.raw_md.write()

    # stage 2: dpsk correct mistakes    
    # <filename-raw>.md -> <filename-formatted>.md
    def _process_raw_to_formatted(self):
        if self.formatted_md.exists:
            print(
                f"File {self.formatted_md.filename} already exists. Skipping raw markdown to formatted markdown conversion.")
            return

        print(f"Stage 1: Processing Markdown file: {self.raw_md.filename} to {self.formatted_md.filename}")

        prompt = FileHandler("prompt_optimize_raw_md.txt")
        prompt_content = prompt.read()
        input = self.raw_md.buffer if self.raw_md.buffer else self.raw_md.read()
        self.formatted_md.buffer = self.processor.process(input, prompt_content)
        self.formatted_md.write()

    # stage 3:  dpsk convert to tex and format math formulae
    # <filename-formatted>.md -> <filename-cheatsheet.tex>
    def _process_formatted_to_tex(self):
        if self.cheatsheet_tex.exists:
            print(
                f"File {self.cheatsheet_tex.filename} already exists. Skipping formatted markdown to LaTeX conversion.")
            return

        print(
            f"Stage 2: Processing simplified Markdown file: {self.formatted_md.filename} to {self.cheatsheet_tex.filename}")
        prompt = FileHandler("prompt_optimize_tex.txt")
        prompt_content = prompt.read()
        input = self.formatted_md.buffer if self.formatted_md.buffer else self.formatted_md.read()
        self.cheatsheet_tex.buffer = self.processor.process(input, prompt_content)
        self.cheatsheet_tex.write()

    # stage 4:
    # <filename-cheatsheet.tex> -> <filename-cheatsheet.pdf> 
    # not provided in this version
    def _render_tex(self):
        # not implementd yet
        src = os.path.join(self.input_dir, os.path.basename(self.cheatsheet_tex.filename))
        dst = os.path.join(self.output_dir, os.path.basename(self.cheatsheet_tex.filename))
        try:
            shutil.copyfile(src, dst)
            print(f"Copied {src} to {dst}")
        except Exception as e:
            print(f"Failed to copy {src} to {dst}: {e}")


if __name__ == "__main__":
    generator = Generator()
    generator.parse_args()
