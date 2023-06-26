import os
import subprocess

from joblib import Parallel, delayed

target_folder = "/net/acadia3a/data/datasets/nuplan"
os.chdir(target_folder)
os.system("ls")


def extract_zip(zip_file):
    os.system(f"tar -xf {zip_file}")
    print(f"Extracted {zip_file}")


if __name__ == "__main__":
    zip_files = ["nuplan-v1.1_train_lidar_{}.zip".format(i) for i in range(1, 44)]  # Assuming 44 zip files from 0 to 43

    # Extract the zip files in parallel
    num_processes = 8  # Adjust this number based on your system's capabilities
    Parallel(n_jobs=num_processes)(delayed(extract_zip)(zip_file) for zip_file in zip_files)
