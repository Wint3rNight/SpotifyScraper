# Spotify Playlist Scraper & Downloader
A Django web application that scrapes a public Spotify playlist and downloads the tracks as MP3 files from YouTube.

## Installation

1. Clone the Repository

git clone <https://github.com/Wint3rNight/SpotifyScraper.git>
cd <repository-folder-name>

2. Set Up a Python Virtual Environment

## Create the virtual environment
```bash
python -m venv venv
```
## Activate the environment
On Windows:
```bash
venv\Scripts\activate
```
On macOS/Linux:
```bash
source venv/bin/activate
```

3. Install System Dependency: FFmpeg

    On macOS (with Homebrew):
```bash
    brew install ffmpeg
```
    On Linux (Debian/Ubuntu):
```bash
    sudo apt update && sudo apt install ffmpeg
```
    On Linux (Arch):
```bash
    sudo pacman -Syu ffmpeg
```
    On Windows:
    Follow the official instructions to download and add FFmpeg to your system's PATH.

4. Install Python Packages

```bash
pip install -r requirements.txt
```
5. Run the Application

```bash
python manage.py runserver
```
Navigate to http://127.0.0.1:8000/ in your web browser.