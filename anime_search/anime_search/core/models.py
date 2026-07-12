from django.db import models

# Create your models here.
class Anime(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Scene(models.Model):
    anime = models.ForeignKey(Anime, related_name="scenes", on_delete=models.CASCADE)
    episode = models.IntegerField()
    title = models.CharField(max_length=255, blank=True)
    embedding = models.JSONField(null=True, blank=True)
    description = models.TextField()
    keywords = models.TextField(help_text="space-separated keywords for search")
    tags = models.TextField(help_text="comma-separated tags (naruto, sasuke, fight...)")
    image = models.ImageField(upload_to="scenes/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.anime.name} ep {self.episode}"

    def get_tags(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]