import argparse
import os
import utils
import zipfile
import tarfile

from typing import List
from joblib import Parallel, delayed
from tqdm import tqdm


def get_all_files(folder_path) -> List[str]:
    """
    Returns a list of all the files in the folder_path. Folders in the folder_path will be ignored.
    The returned files will have a path like "folder_path/file".
    """
    files = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            files.append(file_path)

    return files


def extract_zip(zip_file_path, output_dir):
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Get the list of files to extract.
        file_list = zip_ref.namelist()

        # Create the output directory if it doesn't exist.
        os.makedirs(output_dir, exist_ok=True)

        # Extract files with progress using tqdm.
        for file in tqdm(
            file_list,
            desc=f"Extracting file {zip_file_path} to {output_dir}",
            unit=" files",
        ):
            zip_ref.extract(file, output_dir)


def extract_tar(tar_file_path, output_dir):
    with tarfile.open(tar_file_path, "r") as tar_ref:
        # Get the list of members (files/directories) to extract.
        member_list = tar_ref.getmembers()

        # Create the output directory if it doesn't exist.
        os.makedirs(output_dir, exist_ok=True)

        # Extract members with progress using tqdm.
        for member in tqdm(
            member_list,
            desc=f"Extracting file {tar_file_path} to {output_dir}",
            unit=" members",
        ):
            tar_ref.extract(member, output_dir)


def extract_compressed_files(file: str, output_dir: str):
    """
    Extracts a compressed file. If the file is not ended with ".tgz" or ".zip", report this error and do nothing.
    """
    file_extension = os.path.splitext(file)[-1]

    if file_extension == ".zip":
        extract_zip(file, output_dir)
    elif file_extension == ".tgz":
        extract_tar(file, output_dir)
    else:
        print(f"Unsupported file {file}!")
        return

    print(f"File {file} extracted.")


def main():
    parser = argparse.ArgumentParser(description="Extract compressed files.")
    # Adjust the num_process based on your system's capabilities.
    parser.add_argument("--num_process", type=int, default=8)
    parser.add_argument(
        "--data_output_dir", type=str, default=utils.get_default_data_output_dir()
    )
    args = parser.parse_args()

    data_output_dir = args.data_output_dir
    num_process = args.num_process
    files = get_all_files(data_output_dir)

    Parallel(n_jobs=num_process)(
        delayed(extract_compressed_files)(file, data_output_dir) for file in files
    )


if __name__ == "__main__":
    main()
