import requests
import time
import re
from io import BytesIO
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import Scene


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}


def search_image(query):
    """Search DuckDuckGo images and return the first image URL."""
    try:
        # Get DuckDuckGo vqd token
        r = requests.get(
            "https://duckduckgo.com/",
            params={"q": query},
            headers=HEADERS,
            timeout=10
        )
        match = re.search(r"vqd=([\d-]+)", r.text)
        if not match:
            return None
        vqd = match.group(1)

        # Image search
        r2 = requests.get(
            "https://duckduckgo.com/i.js",
            params={
                "l": "us-en",
                "o": "json",
                "q": query,
                "vqd": vqd,
                "f": ",,,,,",
                "p": "1",
            },
            headers={**HEADERS, "Referer": "https://duckduckgo.com/"},
            timeout=10
        )
        results = r2.json().get("results", [])
        if results:
            return results[0]["image"]
    except Exception as e:
        print(f"  Search error: {e}")
    return None


def download_image(url):
    """Download image bytes from URL."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
            return r.content
    except Exception as e:
        print(f"  Download error: {e}")
    return None


class Command(BaseCommand):
    help = "Fetch images for scenes from DuckDuckGo image search"

    def handle(self, *args, **kwargs):
        scenes = Scene.objects.filter(image="").order_by("id")
        total = scenes.count()
        self.stdout.write(f"Fetching images for {total} scenes...\n")

        for i, scene in enumerate(scenes, 1):
            query = f"{scene.anime.name} episode {scene.episode} scene anime screenshot"
            self.stdout.write(f"[{i}/{total}] Scene {scene.id} — {query[:60]}")

            img_url = search_image(query)
            if not img_url:
                self.stdout.write("  No image found, skipping.")
                time.sleep(1)
                continue

            img_data = download_image(img_url)
            if not img_data:
                self.stdout.write("  Download failed, skipping.")
                time.sleep(1)
                continue

            filename = f"scene_{scene.id}.jpg"
            scene.image.save(filename, ContentFile(img_data), save=True)
            self.stdout.write(f"  Saved: {filename}")

            time.sleep(1.5)  # be polite, avoid rate limiting

        self.stdout.write(self.style.SUCCESS("\nDone!"))
