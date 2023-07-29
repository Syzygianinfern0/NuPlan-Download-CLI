# NuScenes-Download-CLI

This repo provides the scripts to download various datasets in [NuScenes](https://www.nuscenes.org/).

## Usage

### NuPlan

```bash
python download_nuplan.py --username <username> --password <password>
wget -i download_links.txt
```

The URLs should be valid for about five days. If you need to download the files again, just run the script again to generate the URLs. Godspeed with the terrabytes of downloads and good luck choking and hogging your entire team's bandwidth.

### NuScenes

```bash
python download_nuscenes.py --username <username> --password <password>
sh download_commands.txt
```

### Extract the downloaded data

After you download the data, you can extract the download data using the following python script.

```bash
python extract_parallel.py
```

## Why

The NuScenes team for some reason keeps these links behind a convoluted authentation and token expiration system. And that makes downloading them super hard unless you want to keep a browser open for 5 days straight or use a CurlWget extension for 165 different links individually. This script automates that process by reverse engineering the authentation system and capturing the bearer tokens responsible for generating those temporary URLs for download. You can then download those files using wget very easily! Have fun <3