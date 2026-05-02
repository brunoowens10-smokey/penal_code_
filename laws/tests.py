import json

from django.test import TestCase
from django.urls import reverse

from .models import Article, Chapter, Title


class LawsViewsTests(TestCase):
    def setUp(self):
        self.title = Title.objects.create(number="I", name_en="General provisions")
        self.chapter = Chapter.objects.create(
            title=self.title,
            number="1",
            name_en="Criminal liability",
        )
        self.article = Article.objects.create(
            chapter=self.chapter,
            number="57",
            title_en="Theft",
            content_en="A person who commits theft is liable to imprisonment.",
            content_fr="Le vol est puni par une peine d'emprisonnement.",
            content_rw="Ubujura buhanishwa igifungo.",
        )

    def test_home_uses_imported_counts(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1</strong> Articles")
        self.assertContains(response, "General provisions")

    def test_search_finds_article_content(self):
        response = self.client.get(reverse("search"), {"q": "theft"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Article 57")
        self.assertContains(response, "Theft")

    def test_language_switch_changes_article_content(self):
        self.client.get(reverse("set_language"), {"lang": "rw"})
        response = self.client.get(reverse("article_detail", args=[self.article.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ubujura buhanishwa igifungo.")

    def test_assistant_returns_answer_and_sources(self):
        response = self.client.post(
            reverse("assistant"),
            data=json.dumps({"question": "What is the punishment for theft?"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("Article 57", payload["answer"])
        self.assertEqual(payload["sources"][0]["number"], "57")
