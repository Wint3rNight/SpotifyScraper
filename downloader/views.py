from django.shortcuts import render

# Create your views here.
import os
import subprocess


from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common import service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = FirefoxService(FirefoxDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def fetch_playlist_data(driver, playlist_url):
    driver.get(playlist_url)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.[data-testid="tracklist-row"]')
            )
        )
    except Exception as e:
        print(f"Error: Couldn't load the playlist. {e}")
        return []
    song_rows = driver.find_elements(
        By.CSS_SELECTOR, 'div[data-testid="tracklist-row"]'
    )
    tracks = []
    for row in song_rows:
        try:
            title_element = row.find_element(
                By.CSS_SELECTOR, 'a[data-testid="internal-track-link"]'
            )
            song_title = title_element.text
            artist_element = row.find_element(
                By.CSS_SELECTOR, 'span>a[href*="/artist/"]'
            )
            artist_name = artist_element.text
            if song_title and artist_name:
                tracks.append({"title": spng_title, "artist": artist_name})
        except Exception:
            continue
    return tracks


def download_song_from_youtube(title, artist):
    search_query = f"{artist}-{title} audio"
    output_template = f"downloads/{artist}-{title}.mp3"
    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--output",
        output_template,
        "--default-search",
        "ytsearch",
        search_query,
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully downloaded: {artist} - {title}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading {title}: {e.stderr}")


def home_view(request):
    if request.method == "POST":
        playlist_url = request.POST.get("playlist_url")
        driver = setup_driver()
        tracks = fetch_playlist_data(driver, playlist_url)
        driver.quit()
        if tracks:
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            for track in tracks:
                download_song_from_youtube(track["title"], track["artist"])
            message = f"Download complete! {len(tracks)} tracks have been downloaded."
            return render(request, "home.html", {"message": message})
    return render(request, "home.html")
