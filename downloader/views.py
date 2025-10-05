# downloader/views.py

import os
import re
import subprocess
from django.shortcuts import render

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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


def home_view(request):
    if request.method == "POST":
        playlist_url = request.POST.get("playlist_url")

        print("Request received. Setting up driver...")
        driver = setup_driver()

        print(f"Fetching playlist data from: {playlist_url}")
        tracks = fetch_playlist_data(driver, playlist_url)
        driver.quit()

        if tracks:
            print(f"Found {len(tracks)} tracks. Starting downloads...")
            if not os.path.exists("downloads"):
                os.makedirs("downloads")

            for track in tracks:
                download_song_from_youtube(track["title"], track["artist"])

            message = f"Download complete! {len(tracks)} tracks processed. Check the server's 'downloads' folder."
            return render(request, "home.html", {"message": message})
        else:
            message = "Could not find any tracks. The URL might be invalid, the playlist private, or the page structure has changed."
            return render(request, "home.html", {"message": message})

    return render(request, "home.html")
