import json
import re

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import Article, Chapter, Title


SUPPORTED_LANGUAGES = {"en", "fr", "rw"}
STOP_WORDS = {
    "about", "after", "also", "and", "are", "can", "does", "for", "from",
    "has", "have", "how", "into", "law", "laws", "penal", "tell", "that",
    "the", "this", "what", "when", "where", "which", "with", "would",
}


def get_language(request):
    lang = request.session.get("lang", "en")
    return lang if lang in SUPPORTED_LANGUAGES else "en"


def article_text(article, lang):
    if lang == "fr" and article.content_fr:
        return article.content_fr
    if lang == "rw" and article.content_rw:
        return article.content_rw
    return article.content_en


def article_title(article, lang):
    return article.title_en or f"Article {article.number}"


def split_terms(query):
    return [
        term for term in re.findall(r"[A-Za-z0-9']+", query.lower())
        if len(term) > 2 and term not in STOP_WORDS
    ]


def article_queryset():
    return Article.objects.select_related("chapter", "chapter__title").order_by("id")


def search_articles(query):
    terms = split_terms(query)
    if not query:
        return Article.objects.none()

    filters = (
        Q(number__icontains=query)
        | Q(title_en__icontains=query)
        | Q(content_en__icontains=query)
        | Q(content_fr__icontains=query)
        | Q(content_rw__icontains=query)
        | Q(chapter__name_en__icontains=query)
        | Q(chapter__title__name_en__icontains=query)
    )

    for term in terms:
        filters |= (
            Q(title_en__icontains=term)
            | Q(content_en__icontains=term)
            | Q(content_fr__icontains=term)
            | Q(content_rw__icontains=term)
        )

    return article_queryset().filter(filters).distinct()


def ranked_articles(query, lang, limit=5):
    terms = split_terms(query)
    candidates = list(search_articles(query)[:80])

    def score(article):
        haystack = " ".join([
            article.number,
            article.title_en,
            article.content_en,
            article.content_fr,
            article.content_rw,
        ]).lower()
        exact = query.lower() in haystack
        return (12 if exact else 0) + sum(haystack.count(term) for term in terms)

    ranked = sorted(candidates, key=score, reverse=True)
    return [article for article in ranked if score(article) > 0][:limit]


@ensure_csrf_cookie
def home(request):
    titles = Title.objects.prefetch_related("chapters").order_by("id")
    context = {
        "titles": titles,
        "lang": get_language(request),
        "article_count": Article.objects.count(),
        "chapter_count": Chapter.objects.count(),
        "title_count": Title.objects.count(),
    }
    return render(request, "laws/home.html", context)


@ensure_csrf_cookie
def title_detail(request, title_id):
    title = get_object_or_404(Title, id=title_id)
    chapters = title.chapters.prefetch_related("articles").order_by("id")
    return render(request, "laws/title_detail.html", {
        "title": title,
        "chapters": chapters,
        "lang": get_language(request),
    })


@ensure_csrf_cookie
def chapter_detail(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)
    articles = chapter.articles.all().order_by("id")
    return render(request, "laws/chapter_detail.html", {
        "chapter": chapter,
        "articles": articles,
        "lang": get_language(request),
    })


@ensure_csrf_cookie
def article_detail(request, article_id):
    article = get_object_or_404(article_queryset(), id=article_id)
    lang = get_language(request)
    return render(request, "laws/article_detail.html", {
        "article": article,
        "article_content": article_text(article, lang),
        "article_heading": article_title(article, lang),
        "lang": lang,
    })


@ensure_csrf_cookie
def search(request):
    query = request.GET.get("q", "").strip()
    lang = get_language(request)
    results = search_articles(query) if query else []
    return render(request, "laws/search.html", {
        "results": results,
        "query": query,
        "lang": lang,
    })


@require_POST
def assistant(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        payload = {}

    question = str(payload.get("question", "")).strip()
    lang = get_language(request)
    if len(question) < 3:
        return JsonResponse({
            "answer": "Ask a fuller question so I can search the Penal Code for the most relevant articles.",
            "sources": [],
        })

    matches = ranked_articles(question, lang)
    if not matches:
        return JsonResponse({
            "answer": "I could not find a matching article in the Penal Code. Try a different keyword, offence, or article number.",
            "sources": [],
        })

    lead = matches[0]
    lead_text = article_text(lead, lang)
    answer = (
        f"The closest match is Article {lead.number}, \"{article_title(lead, lang)}\". "
        f"{lead_text[:520].strip()}"
    )
    if len(lead_text) > 520:
        answer += "..."

    sources = [
        {
            "number": article.number,
            "title": article_title(article, lang),
            "url": reverse("article_detail", args=[article.id]),
            "excerpt": article_text(article, lang)[:220].strip(),
        }
        for article in matches
    ]
    return JsonResponse({"answer": answer, "sources": sources})


def set_language(request):
    lang = request.GET.get("lang", "en")
    request.session["lang"] = lang if lang in SUPPORTED_LANGUAGES else "en"
    return redirect(request.META.get("HTTP_REFERER", "/"))
