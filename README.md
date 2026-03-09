# img-convert

A high-performance, multi-threaded image conversion tool built with Python and Pillow. It supports batch processing and single-file conversions with intelligent color mode handling.

## Features
* **Batch Conversion:** Convert entire directories of images simultaneously.
* **Parallel Processing:** Uses `ProcessPoolExecutor` to utilize all CPU cores for faster throughput.
* **Intelligent Color Conversion:** Automatically detects and converts color modes (e.g., RGBA to RGB) to ensure compatibility with the target format.
* **Path Safety:** Built using `pathlib` for robust cross-platform path handling.
* **Preserving EXIF Data:** EXIF data can be preserved accross conversions with the `--copyexif` or `-c` flag
* **Scrub EXIF Data mode:** The `remove-exif` or `re` mode makes a copy of the original image with the EXIF data removed

## Requirements
* Python 3.x
* Pillow (`pip install pillow`)

## Usage

### Batch convert a directory
```bash
python img-convert.py batch <input_directory> <output_format>
```
### Single file conversion
```bash
python img-convert.py file <input_file> <output_file>
```
### Removing EXIF data
```bash
python img-convert.py remove-exif <input_file>
```
