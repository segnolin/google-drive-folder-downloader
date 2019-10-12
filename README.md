# google-drive-folder-downloader

Download Google Drive folder without zipping!

## Getting Started

You need to enable the Drive API to use the script.
The enabling instructions can be found on [Python Quickstart](https://developers.google.com/drive/api/v3/quickstart/python).<br/>
The `credentials.json` file will be needed in the working directory.

## Basic Usage

Just run the script with target folder name and the destination path (optional, default value is `./`) where you want to save to.

### Python 3.6+

```
$ python3 download.py folder_name [path]
```

### Python 2.7

```
$ python download-2.py folder_name [path]
```
