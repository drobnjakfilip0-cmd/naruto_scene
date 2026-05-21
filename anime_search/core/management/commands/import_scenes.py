import json
from pathlib import Path

from django.core.management.base import BaseCommand
from core.models import Anime, Scene
from core.utils.embeddings import get_embedding


class Command(BaseCommand):
    help = "Import scenes from JSON dataset"

    def handle(self, *args, **kwargs):

        BASE_DIR = Path(__file__).resolve().parents[3]
        json_path = BASE_DIR / "data" / "scenes.json"

        self.stdout.write(f"Loading: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        created_count = 0

        for item in data:

            # -----------------------
            # Anime
            # -----------------------
            anime_name = item["anime"]

            anime, _ = Anime.objects.get_or_create(
                name=anime_name,
                defaults={
                    "slug": anime_name.lower().replace(" ", "-")
                }
            )

            # -----------------------
            # Embedding text
            # -----------------------
            text_for_embedding = (
                item["description"]["en"] + " " +
                item["keywords"]["en"] + " " +
                " ".join(item["tags"])
            )

            # -----------------------
            # Scene
            # -----------------------
            Scene.objects.create(
                anime=anime,
                episode=item["episode"],
                title="",

                description=item["description"]["en"],
                keywords=item["keywords"]["en"],
                tags=",".join(item["tags"]),

                embedding=get_embedding(text_for_embedding)
            )

            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {created_count} scenes successfully."
            )
        )