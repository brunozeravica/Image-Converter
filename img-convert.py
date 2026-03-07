from PIL import Image
import sys
from pathlib import Path
import argparse
import io
import random
import string

def main():
    
    parser = argparse.ArgumentParser(
                        prog="img-convert",
                        description="Converts either an image or an entire directory of images from one format to another.")

    parser.add_argument("-b", "--batch", action="store_true", help="Batch convert")
    parser.add_argument("vars", nargs="*", help="Files/directories for conversion")

    args = parser.parse_args()


    if args.batch:
        if len(args.vars) != 2:
            sys.exit("Error: --batch(-b) requires exactly 2 arguments, an input directory and an output file format")

        output_file_format = args.vars[1].upper().strip().replace(".", "")
        input_dir = Path(args.vars[0])

        if not input_dir.is_dir():
            sys.exit(f"Batch mode requires a directory as input, got: {args.vars[0]}")

        # Generating a random directory name so as not to overwrite an existing one
        while True:
            random_name = "".join(random.choices(string.ascii_letters, k=6)) + "_converted"
            output_dir = input_dir / random_name
            if not output_dir.exists():
                break

        output_dir.mkdir(parents=True)

        supported_exts = Image.registered_extensions()
        for file in input_dir.iterdir():
            if file.is_file() and file.suffix.lower() in supported_exts:
                output_file = Path(output_dir / (file.stem + "." + output_file_format))
                convert_image(file, output_file)

    else:
        if len(args.vars) != 2:
            sys.exit("Error: file conversion requires exactly 2 arguments, an input file and an output file")

        convert_image(args.vars[0], args.vars[1])

    return


def convert_image(input_file: Path, output_file: Path):

    try:
        input_file = Path(input_file)
        output_file = Path(output_file)

    except Exception as e:
        sys.exit(f"Invalid path, Error: {e}")

    # Get the extension of the output file
    output_file_format = output_file.suffix.upper().replace(".", "")
    if output_file_format == "JPG": output_file_format = "JPEG"

    try:
        with Image.open(input_file) as img:
            # Check if the output file format can save an image in the color mode of the input image
            if not file_format_mode_check(output_file_format, img.mode):
                if file_format_mode_check(output_file_format, "RGBA"):
                    img = img.convert("RGBA")

                else:
                    img = img.convert("RGB")

            if output_file_format not in Image.SAVE.keys():
                print(f"Unsupported file format: {output_file_format}")
                return

            img.save(output_file)

    except Exception as e:
        print(f"Skipping {input_file}: {e}")
        return

    print(f"Successfully converted {input_file} to {output_file}")
    return

def file_format_mode_check(file_format, required_mode):

    try:
        img = Image.new(required_mode, (1, 1))
        buffer = io.BytesIO()
        img.save(buffer, format=file_format)
        return True

    except Exception:
        return False


if __name__ == "__main__":
    main()
