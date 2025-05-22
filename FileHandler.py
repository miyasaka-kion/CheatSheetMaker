from pathlib import Path
import json
import aiofiles
import asyncio
from typing import Optional, Union, Dict, Any

class FileHandler:
    def __init__(self, filepath: str):
        """Initialize with file path without creating any files/directories.
        
        Args:
            filepath: Relative or absolute path to target file.
        """
        self.path = Path(filepath).absolute()
        self.buffer: Optional[str] = None

    # ----- Property Accessors -----
    @property
    def filename(self) -> str:
        """Get filename with extension."""
        return self.path.name
    
    @property
    def base(self) -> str:
        """Get filename without extension."""
        return self.path.stem
    
    @property
    def exists(self) -> bool:
        """Check if file exists."""
        return self.path.exists()
    
    # @property
    # def path_string(self) -> str:
    #     """Get absolute path."""
    #     return str(self.path)

    # ----- Synchronous Operations -----
    def read(self) -> str:
        """Read file content synchronously.
        
        Raises:
            FileNotFoundError: If file doesn't exist.
        """
        if not self.exists:
            raise FileNotFoundError(f"File not found: {self.path}")
        with open(self.path, 'r', encoding='utf-8') as f:
            return f.read()
        
    def write(self, content: Optional[str] = None) -> None:
        """Write content or buffer to file synchronously.

        If content is not provided, writes self.buffer.
        Creates parent directories if needed.
        """
        data = content if content is not None else self.buffer
        if data is None:
            raise ValueError("No content or buffer to write.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(data)

    # ----- Asynchronous Operations -----
    async def async_write(self, content: Optional[str] = None) -> None:
        """Write content or buffer to file asynchronously.

        If content is not provided, writes self.buffer.
        Uses aiofiles for non-blocking I/O operations.
        """
        data = content if content is not None else self.buffer
        if data is None:
            raise ValueError("No content or buffer to write.")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.path, 'w', encoding='utf-8') as f:
            await f.write(data)

 

if __name__ == "__main__":
    # Example usage
    file_handler = FileHandler("input/example.txt")
    print(f"File exists: {file_handler.exists}")

    file_handler.write("Hello, World!")
    print(file_handler.read())
    print(f"File exists: {file_handler.exists}")