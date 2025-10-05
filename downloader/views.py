# downloader/views.py

import os
import re
import subprocess
import threading
from django.shortcuts import render
from django.http import JsonResponse


from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

download_progress = {
    "status": "idle",
    "total_songs": 0,
    "download_count": 0,
    "message": "Downloading...",
}


def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def fetch_playlist_data(driver, url):
    driver.get(url)
    try:
        wait = WebDriverWait(driver, 60)
        container_selector = 'div[data-testid="playlist-tracklist"]'
        container = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, container_selector))
        )
        row_selector = 'div[data-testid="tracklist-row"]'
        song_rows = container.find_elements(By.CSS_SELECTOR, row_selector)

        print(f"Found {len(song_rows)} song rows. Extracting data...")
        tracks = []
        for row in song_rows:
            try:
                title_element = row.find_element(
                    By.CSS_SELECTOR, 'a[data-testid="internal-track-link"]'
                )
                song_title = title_element.text
                artist_element = row.find_element(
                    By.CSS_SELECTOR, 'a[href*="/artist/"]'
                )
                artist_name = artist_element.text
                if song_title and artist_name:
                    tracks.append({"title": song_title, "artist": artist_name})
            except Exception:
                continue
        print(f"Successfully extracted {len(tracks)} tracks.")
        return tracks

    except Exception as e:
        print(f"Error fetching playlist content: {e}")
        return []


def download_song_from_youtube(title, artist):
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    safe_artist = re.sub(r'[\\/*?:"<>|]', "", artist)
    search_query = f"{artist} {title} official audio"
    output_template = f"downloads/{safe_artist} - {safe_title}.mp3"
    print(f"Downloading: {artist} - {title}")
    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--output",
        output_template,
        f"ytsearch1:{search_query}",
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully downloaded: {artist} - {title}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {title}: {e.stderr.strip()}")


def download_thread_target(playlist_url):
    global download_progress
    download_progress["status"] = "scraping"
    driver = setup_driver()
    tracks = fetch_playlist_data(driver, playlist_url)
    driver.quit()
    if not tracks:
        download_progress["status"] = "error"
        return
    download_progress["total_songs"] = len(tracks)
    download_progress["status"] = "downloading"
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    for i, track in enumerate(tracks):
        download_song_from_youtube(track['title'], track['artist'])
        download_progress['downloaded_count'] = i + 1
    download_progress['status'] = 'complete'


def home_view(request):
    global download_progress
    if request.method == "POST":
        playlist_url = request.POST.get("playlist_url")
        thread=threading.Thread(target=download_thread_target, args=(playlist_url,))
        thread.start()
        return render(request,'progress.html')
    return render(request,'home.html')
    
def check_progress(request):
    global download_progress
    return JsonResponse(download_progress)
        
       