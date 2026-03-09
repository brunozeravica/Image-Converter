# img-convert

A high-performance, multi-process image conversion tool built with **Python** and **Pillow**.  
It supports **single-file conversions**, **batch processing**, optional **EXIF preservation**, and **flexible image resizing**.

## Features

* **Batch Conversion**  
  Convert entire directories of images in one command.

* **Parallel Processing**  
  Uses `ProcessPoolExecutor` to utilize multiple CPU cores for faster conversion.

* **Single File Conversion**  
  Convert individual images with precise control over the output file.

* **Intelligent Color Mode Handling**  
  Automatically converts color modes (e.g. `RGBA → RGB`) when the target format does not support the original mode.

* **EXIF Metadata Preservation**  
  Use `--copyexif` (`-c`) to retain the original image metadata.

* **EXIF Removal Mode**  
  The `remove-exif` (`re`) command creates a copy of an image with all EXIF metadata removed.

* **Flexible Resizing**  
  Resize images using multiple scaling strategies (`contain`, `cover`, `fit`, `force`).

* **Safe File Handling**  
  Uses `pathlib` for robust cross-platform path handling.

* **Progress Indicator**  
  Batch mode shows a progress bar using `tqdm` (unless verbose mode is enabled).

* **Verbose Output**  
  Use `-v` to display detailed conversion logs.

---

# Requirements

* Python **3.10+** (for `match` syntax)
* Pillow
* tqdm

# Usage

## Batch convert a directory

Convert all supported images inside a directory.

```bash
python img-convert.py batch <input_directory> <output_format>
```

Example:

```bash
python img-convert.py batch photos png
```

This creates a new output directory:

```
photos_converted_<timestamp>_<random>
```

inside the input directory.

---

## Single file conversion

Convert one image to another format.

```bash
python img-convert.py file <input_file> <output_file>
```

## Removing EXIF metadata

Create a copy of an image with its EXIF data removed.

```bash
python img-convert.py remove-exif <input_file>
```

Example:

```bash
python img-convert.py remove-exif photo.jpg
```

This creates a file similar to:

```
noexif_<timestamp>_<random>_photo.jpg
```

---

# Resize Images

The `--resize` (`-r`) flag allows resizing images during conversion.

Syntax:

```
--resize <mode> <width>x<height>
```

Example:

```bash
python img-convert.py file input.png output.jpg --resize fit 800x600
```

## Resize Modes

| Mode | Description |
|-----|-------------|
| **contain** | Scales the image to fit within the target dimensions while preserving aspect ratio |
| **cover** | Scales the image to completely fill the target dimensions, cropping if necessary |
| **fit** | Crops and resizes the image to exactly match the specified size |
| **force** | Forces the image to the exact dimensions without preserving aspect ratio |

# Options

| Flag | Description |
|-----|-------------|
| `-c`, `--copyexif` | Preserve EXIF metadata |
| `-v`, `--verbose` | Enable verbose output |
| `-r`, `--resize` | Resize images during conversion |
