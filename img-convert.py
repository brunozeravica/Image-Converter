import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import io
from pathlib import Path
from PIL import Image, ImageOps
import re
import secrets
import sys
import time
from tqdm import tqdm

def main():

    parser = argparse.ArgumentParser(
                        prog="img-convert",
                        description="Converts images from one format to another.")

    parser.add_argument( "-c", "--copyexif", action="store_true", help="Converted images retain the original EXIF data (metadata)")
    parser.add_argument( "-v", "--verbose", action="store_true", help="Enables verbose output")

    sub = parser.add_subparsers(dest="command", required=True)

    file_cmd = sub.add_parser("file", aliases=["F", "f"],help="Convert a single file (supports -r/--resize)")
    add_resize_args(file_cmd)
    file_cmd.add_argument("input")
    file_cmd.add_argument("output")

    file_cmd.set_defaults(func=convert_single)

    batch_cmd = sub.add_parser("batch", aliases=["B", "b"], help="Batch convert an entire directory (supports -r/--resize)")
    add_resize_args(batch_cmd)
    batch_cmd.add_argument("input_directory")
    batch_cmd.add_argument("output_format")

    batch_cmd.set_defaults(func=convert_batch)

    remove_exif_cmd = sub.add_parser("remove-exif", aliases=["RE", "re"], help="Create a copy of an image without the EXIF data")
    remove_exif_cmd.add_argument("input")

    remove_exif_cmd.set_defaults(func=remove_exif)

    args = parser.parse_args()

    args.func(args)


def add_resize_args(p):
        p.add_argument(
            "-r", "--resize",
            nargs=2,
            metavar=('MODE', 'SIZE'),
            help="Resize mode (contain, cover, fit, force) and dimensions (e.g. --resize fit 600x900)"
        )


def convert_image(input_file: Path, output_file: Path, verbose: bool, exif: bool, size: tuple, mode: str):

    try:
        input_file = Path(input_file)
        output_file = Path(output_file)

    except Exception as e:
        sys.exit(f"Error: Invalid path: {e}")

    if not output_file.suffix:
        print("Invalid file name")
        return False

    exif_data = None
    # Get the extension of the output file
    output_file_format = output_file.suffix.upper().replace(".", "")
    if output_file_format == "JPG": output_file_format = "JPEG"
    try:
        with Image.open(input_file) as img:

            if output_file_format not in Image.SAVE.keys():
                sys.exit(f"Error: Unsupported file format: {output_file_format}")

            if exif:
                exif_data = img.getexif()
            # Check if the output file format can save an image in the color mode of the input image
            if not file_format_mode_check(output_file_format, img.mode):
                for color_mode in ("RGBA", "RGB", "L"):
                    if file_format_mode_check(output_file_format, color_mode):
                        img = img.convert(color_mode)
                        print(f"Forced to convert {input_file.name} to color format {color_mode}")
                        break

            if size:
                match mode:
                    case "contain":
                        img = ImageOps.contain(img, size)
                    case "cover":
                        img = ImageOps.cover(img, size)
                    case "fit":
                        img = ImageOps.fit(img, size)
                    case "force":
                        img = img.resize(size)
                    case _:
                        print(f"Warning: Unknown resize mode '{mode}'. Skipping resize.")

            if exif:
                img.save(output_file, exif=exif_data)

            else:
                img.save(output_file)

    except Exception as e:
        if verbose:
            print(f"Skipping {input_file}: {e}")
        return False

    if verbose:
        print(f"Successfully converted {input_file} to {output_file}")
        
    return True


def convert_single(args):

    input_path = Path(args.input).resolve()
    input_dir = input_path.parent
    output_path = input_dir / args.output

    mode = None
    size = None

    if args.resize:
        mode, size = args.resize
        size = size_regex(size)

    if not convert_image(input_path, output_path, args.verbose, args.copyexif, size, mode):
        print(f"Warning: {input_path} failed to convert")


def convert_batch(args):

    start_time = time.time()

    output_file_format = args.output_format.upper().strip().replace(".", "")
    input_dir = Path(args.input_directory).resolve()

    if not input_dir.is_dir():
        sys.exit(f"Error: Batch mode requires a directory as input, got: {args.input_directory}")

    # Generating a random directory name so as not to overwrite an existing one
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    suffix = secrets.token_hex(2)
    output_dir = f"{input_dir.name}_converted_{timestamp}_{suffix}"
    output_path = input_dir / output_dir
    try:
        output_path.mkdir(parents=True, exist_ok=False)

    except Exception as e:
        sys.exit(f"Error: {e}")

    mode = None
    size = None

    if args.resize:
        mode, size = args.resize
        size = size_regex(size)

    supported_exts = set(Image.registered_extensions().keys())
    files_to_convert = [f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_exts]

    tasks = []
    for file in files_to_convert:
        output_file = output_path / (file.stem + "." + output_file_format)
        tasks.append((file, output_file, args.verbose, args.copyexif, size, mode))

    with ProcessPoolExecutor() as executor:
        if args.verbose:
            results = list(executor.map(parallel, tasks))

        else:
            results = list(tqdm(executor.map(parallel, tasks), total=len(tasks)))

    failed = results.count(False)
    if failed:
        print(f"Warning: {failed}/{len(tasks)} files failed to convert")

    end_time = time.time()
    if args.verbose:
        print(f"Time taken: {end_time - start_time:.2f} seconds")


def parallel(args_tuple):

    input_file, output_file, verbose, exif, size, mode = args_tuple
    return convert_image(input_file, output_file, verbose, exif, size, mode)


def remove_exif(args):

    input_path = Path(args.input).resolve()
    input_dir = input_path.parent

    if args.copyexif and args.verbose:
        print("--copyexif (-c) flag has no functionality in remove-exif mode")

    # Generating a random file name so as not to overwrite an existing one
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    suffix = secrets.token_hex(2)
    output_path = input_dir / f"noexif_{timestamp}_{suffix}_{Path(args.input).name}"
    args.copyexif = False
    mode = None
    size = None
    convert_image(input_path, output_path, args.verbose, args.copyexif, size, mode)


def size_regex(resize):

    pattern = r"^\d{1,4}[x,]{1}\d{1,4}$"
    if not re.search(pattern, resize):
        sys.exit(f"Error: '{resize}' is not a valid resolution (e.g. 600x900)")

    parts = re.split(r'x|,', resize)

    width, height = map(int, parts)
    if height == 0 or width == 0:
        sys.exit("Error: Dimensions must be greater than zero.")

    return width, height


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
