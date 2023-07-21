import argparse
import json

import requests
from joblib import Parallel, delayed
from tqdm import tqdm

# The URL prefix of the NuScenes dataset. Fetched from the request url.
BASE_URL = "https://o9k5xn5546.execute-api.us-east-1.amazonaws.com/v1/archives/v1.0/"


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


def get_download_url(token, url):
    headers = {
        "authorization": "Bearer " + token,
    }

    # From the same source as BASE_URL.
    params = {
        "region": "us",
        "project": "nuScenes",
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
    )

    download_url = json.loads(response.content)["url"]

    return download_url


def main():
    parser = argparse.ArgumentParser(description="Download nuPlan dataset")
    parser.add_argument("--username")
    parser.add_argument("--password")
    args = parser.parse_args()

    # requests session
    with requests.Session() as s:
        # login and get auth token
        login_token = login(args.username, args.password)

        # ====================
        # NuScenes Trainval Set
        # ====================
        links = [BASE_URL + f"v1.0-trainval{i:02d}_blobs.tgz" for i in range(1, 11)]

        # Metadata
        links += [BASE_URL + "v1.0-trainval_meta.tgz"]

        # ====================
        # NuScenes Test Set
        # ====================
        links += [BASE_URL + "v1.0-test_blobs.tgz"]

        # Metadata
        links += [BASE_URL + "v1.0-test_meta.tgz"]

        # ====================
        # Shared data
        # ====================
        # CAN bus expansion
        links += [BASE_URL + "can_bus.zip"]

        # Map expansion (v1.3)
        links += [BASE_URL + "nuScenes-map-expansion-v1.3.zip"]

        download_links = Parallel(n_jobs=12)(delayed(get_download_url)(login_token, link) for link in tqdm(links))

        # write download links to file
        with open("download_links.txt", "w") as f:
            for link in download_links:
                f.write(link + "\n")


if __name__ == "__main__":
    main()
