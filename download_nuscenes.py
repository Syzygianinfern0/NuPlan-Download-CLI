import argparse
import json
import requests
import utils

from joblib import Parallel, delayed
from tqdm import tqdm


def login(username, password):
    headers = {
        "content-type": "application/x-amz-json-1.1",
        "x-amz-target": "AWSCognitoIdentityProviderService.InitiateAuth",
    }

    data = (
        '{"AuthFlow":"USER_PASSWORD_AUTH","ClientId":"7fq5jvs5ffs1c50hd3toobb3b9","AuthParameters":{"USERNAME":"'
        + username
        + '","PASSWORD":"'
        + password
        + '"},"ClientMetadata":{}}'
    )

    response = requests.post(
        "https://cognito-idp.us-east-1.amazonaws.com/",
        headers=headers,
        data=data,
    )

    token = json.loads(response.content)["AuthenticationResult"]["IdToken"]

    return token


def get_download_url(token, file_name):
    # The URL prefix of the NuScenes dataset. Fetched from the request url.
    BASE_URL = (
        "https://o9k5xn5546.execute-api.us-east-1.amazonaws.com/v1/archives/v1.0/"
    )

    headers = {
        "authorization": "Bearer " + token,
    }

    # From the same source as BASE_URL.
    params = {
        "region": "us",
        "project": "nuScenes",
    }

    url = BASE_URL + file_name
    response = requests.get(
        url,
        params=params,
        headers=headers,
    )

    download_url = json.loads(response.content)["url"]

    return download_url


def main():
    parser = argparse.ArgumentParser(description="Download nuScenes dataset")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument(
        "--data_output_dir", type=str, default=utils.get_default_data_output_dir()
    )
    args = parser.parse_args()

    data_output_dir = args.data_output_dir
    # requests session
    with requests.Session() as s:
        # login and get auth token
        login_token = login(args.username, args.password)

        # ====================
        # NuScenes Trainval Set
        # ====================
        file_names = [f"v1.0-trainval{i:02d}_blobs.tgz" for i in range(1, 11)]

        # Metadata
        file_names += ["v1.0-trainval_meta.tgz"]

        # ====================
        # NuScenes Test Set
        # ====================
        file_names += ["v1.0-test_blobs.tgz"]

        # Metadata
        file_names += ["v1.0-test_meta.tgz"]

        # ====================
        # NuScenes Mini 
        # ====================
        file_names += ["v1.0-mini.tgz"]

        # ====================
        # Shared data
        # ====================
        # CAN bus expansion
        file_names += ["can_bus.zip"]

        # Map expansion (v1.3)
        file_names += ["nuScenes-map-expansion-v1.3.zip"]

        download_links = Parallel(n_jobs=12)(
            delayed(get_download_url)(login_token, file_name)
            for file_name in tqdm(file_names)
        )

        # write download commands to file
        with open("download_commands.txt", "w") as f:
            # a command to create the output directory if it does not exist.
            f.write(f"mkdir -p {data_output_dir}\n")
            # a command to enter the output directory.
            f.write(f"cd {data_output_dir}\n")
            # commands to download each file.
            for i in range(len(download_links)):
                command = f'wget -O {file_names[i]} "{download_links[i]}"\n'
                f.write(command)


if __name__ == "__main__":
    main()
