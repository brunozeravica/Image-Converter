from PIL import Image
import sys
from pathlib import Path
import argparse
import io
import secrets
import string
from concurrent.futures import ProcessPoolExecutor
import time
from datetime import datetime

def main():

    parser = argparse.ArgumentParser(
                        prog="img-convert",
                        description="Converts images from one format to another.")

    sub = parser.add_subparsers(dest="command", required=True)

    file_cmd = sub.add_parser("file", aliases=["F"],help="Convert a single file")
    file_cmd.add_argument("input")
    file_cmd.add_argument("output")

    file_cmd.set_defaults(func=convert_single)

    batch_cmd = sub.add_parser("batch", aliases=["B"], help="Batch convert an entire directory")
    batch_cmd.add_argument("input_directory")
    batch_cmd.add_argument("output_format")

    batch_cmd.set_defaults(func=convert_batch)

    args = parser.parse_args()

    args.func(args)


def parallel(pair):

    input_file, output_file = pair
    return convert_image(input_file, output_file)


def convert_image(input_file: Path, output_file: Path):

    try:
        input_file = Path(input_file)
        output_file = Path(output_file)

    except Exception as e:
        sys.exit(f"Invalid path, Error: {e}")

    if not output_file.suffix:
        sys.exit("Invalid file name")

    # Get the extension of the output file
    output_file_format = output_file.suffix.upper().replace(".", "")
    if output_file_format == "JPG": output_file_format = "JPEG"
    try:
        with Image.open(input_file) as img:
            # Check if the output file format can save an image in the color mode of the input image
            if not file_format_mode_check(output_file_format, img.mode):
                for mode in ("RGBA", "RGB", "L"):
                    if file_format_mode_check(output_file_format, mode):
                        img = img.convert(mode)
                        break

            if output_file_format not in Image.SAVE.keys():
                print(f"Unsupported file format: {output_file_format}")
                return

            img.save(output_file)

    except Exception as e:
        print(f"Skipping {input_file}: {e}")
        return

    print(f"Successfully converted {input_file} to {output_file}")


def convert_single(args):

    input_path = Path(args.input).resolve()
    input_dir = input_path.parent
    output_path = input_dir / args.output

    convert_image(input_path, output_path)


def convert_batch(args):

    start_time = time.time()

    output_file_format = args.output_format.upper().strip().replace(".", "")
    input_dir = Path(args.input_directory).resolve()

    if not input_dir.is_dir():
        sys.exit(f"Batch mode requires a directory as input, got: {args.input_directory}")

    # Generating a random directory name so as not to overwrite an existing one
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    suffix = secrets.token_hex(2)
    output_dir = f"{input_dir.name}_converted_{timestamp}_{suffix}"
    output_path = input_dir / output_dir
    try:
        output_path.mkdir(parents=True, exist_ok=False)

    except Exception as e:
        sys.exit(f"Error: {e}")

    supported_exts = set(Image.registered_extensions().keys())
    files_to_convert = [
    f for f in input_dir.iterdir()
    if f.is_file() and f.suffix.lower() in supported_exts
    ]

    tasks = []
    for file in files_to_convert:
        output_file = output_path / (file.stem + "." + output_file_format)
        tasks.append((file, output_file))

    with ProcessPoolExecutor() as executor:
        list(executor.map(parallel, tasks))

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f}")


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
