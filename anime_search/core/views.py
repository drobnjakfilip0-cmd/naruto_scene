from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse

from .models import Scene
from core.utils.embeddings import get_embedding

import numpy as np


# -----------------------
# HELPERS
# -----------------------
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# -----------------------
# MAIN PAGE (SEARCH UI)
# -----------------------
def index(request):
    query = request.GET.get("query", "").strip()
    scenes = []
    
    if query:

        query_vec = get_embedding(query)

        all_scenes = Scene.objects.exclude(embedding__isnull=True)

        scored = []

        for scene in all_scenes:
            score = cosine_similarity(query_vec, scene.embedding)
            scored.append((score, scene))

        scored.sort(reverse=True, key=lambda x: x[0])

        best_score = scored[0][0] if scored else 0

        if best_score >= 0.30:
            scenes = scored[:3]

    

    return render(request, "core/index.html", {
        "query": query,
        "scenes": scenes
    })


# -----------------------
# OPTIONAL API (ako hoćeš frontend JS kasnije)
# -----------------------
def semantic_search(request):
    query = request.GET.get("query", "").strip()

    if not query:
        return JsonResponse([], safe=False)

    query_vec = get_embedding(query)

    all_scenes = Scene.objects.exclude(embedding__isnull=True)

    scored = []

    for scene in all_scenes:
        score = cosine_similarity(query_vec, scene.embedding)
        scored.append((score, scene))

    scored.sort(reverse=True, key=lambda x: x[0])

    top = scored[:5]

    return JsonResponse([
        {
            "id": s.id,
            "anime": s.anime.name,
            "episode": s.episode,
            "description": s.description,
            "score": float(score)
        }
        for score, s in top
    ], safe=False)


def scene_detail(request, scene_id):
    scene = get_object_or_404(Scene, id=scene_id)

    return render(request, 'core/scene_detail.html', {
        'scene': scene
    })