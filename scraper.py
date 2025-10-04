import time
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.wpewebkit.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    return driver


def fetch_playlist_data(driver, playlist_url):
    driver.get(playlist_url)
    try:
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'div[data-testid="tracklist-row"]')
            )
        )
    except Exception as e:
        print(f"Error: Could not loud the playlist content. {e}")
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
                By.CSS_SELECTOR, 'span > a[href*="/artist/"]'
            )
            artist_name = artist_element.text

            if song_title and artist_name:
                tracks.append({"title": song_title, "artist": artist_name})
        except Exception:
            continue

    return tracks


def download_song_from_youtube(title, artist):
    search_query = f"{artist}-{title} audio"
    output_template = f"downloads/{artist}-{title}.mp3"
    print(f"Downloading {title} by {artist}...")
    command = [
        "yt-dlp",
        "extract-audio",
        "--audio-format",
        "mp3",
        "--audio-quality",
        "0",
        "--output",
        output_template,
        "default-search",
        "ytsearch",
        search_query,
    ]
    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error downloading {title}: {stderr.decode()}")
        else:
            print(f"Successfully downloaded: {artist} - {title}")

    except Exception as e:
        print(f"An exception occurred while downloading {title}: {e}")


if __name__ == "__main__":
    playlist_url = "https://open.spotify.com/playlist/37i9dQZEVXbNG2L3SPXyCG"

    print("Setting up browser driver...")
    driver = setup_driver()

    print(f"Fetching track data from {playlist_url}...")
    tracks = fetch_playlist_data(driver, playlist_url)

    driver.quit()

    if tracks:
        print(f"Found {len(tracks)} tracks. Starting download process...")
        import os

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        for track in tracks:
            download_song_from_youtube(track["title"], track["artist"])
        print("All downloads complete.")
    else:
        print("No tracks were found or an error occurred.")
