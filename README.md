# Very Simple Cheatsheet Generator

A tool for making cheatsheet from lecture slides.

## Features

- Extracts and organizes key information into cheatsheets
- Easy integration with existing workflows
- No context, for simple task only.

## How it works

```mermaid
graph LR
    A[Slides.pdf] -- Convert with marker --> B[text.md]
    B -- Correct wrong format with dpsk -->C[formatted.md]
    C -- simplify and convert with dpsk --> D[cheatsheet.tex]
    D -- Render --> E[cheatsheet.pdf]
```



## Installation

```bash
conda create -n parsedoc python=3.12
```

```bash
git clone https://github.com/yourusername/parsedoc.git
cd parsedoc
pip install -r requirements.txt
```

## Usage

If you have serveral pdf files, merge them into one using PDFsam.

```bash
python Generator.py <input_file>.pdf
```

In current version, the output is a tex file, you can format the output using https://wch.github.io/latexsheet/.

we will (probably) implement the render tex parts in the future.

## Limitations

-   Currently only support, and only test on `deepseek-v3-250324 | Volcengine`

-   Currently only tested on macOS

    

## TODO

- Process different chunks asynchronously.
- Add more language support.
- ?Add image support?
- ?ZH support?
- async file write support.
