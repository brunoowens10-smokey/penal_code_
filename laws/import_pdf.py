import os
import sys
import django
import json

sys.path.append(r'C:\Users\lily\Desktop\penal_code')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'penal_code.settings')
django.setup()

from laws.models import Title, Chapter, Article

# ── Path to articles.json ──────────────────────────────────────────────────
JSON_PATH = r'C:\Users\lily\Desktop\articles.json'
# ──────────────────────────────────────────────────────────────────────────

def run():
    print("Clearing old data...")
    Article.objects.all().delete()
    Chapter.objects.all().delete()
    Title.objects.all().delete()

    with open(JSON_PATH, encoding='utf-8') as f:
        articles = json.load(f)

    titles   = {}
    chapters = {}

    for a in articles:
        # Get or create Title
        t_key = a['title_num']
        if t_key not in titles:
            title_obj, _ = Title.objects.get_or_create(
                number=t_key,
                defaults={'name_en': a['title_name']}
            )
            titles[t_key] = title_obj
            print(f"  Title {t_key}: {a['title_name'][:50]}")

        # Get or create Chapter
        c_key = f"{t_key}_{a['chapter_num']}"
        if c_key not in chapters:
            chapter_obj, _ = Chapter.objects.get_or_create(
                number=a['chapter_num'],
                title=titles[t_key],
                defaults={'name_en': a['chapter_name']}
            )
            chapters[c_key] = chapter_obj
            print(f"    Chapter {a['chapter_num']}: {a['chapter_name'][:50]}")

        # Create Article
        Article.objects.get_or_create(
            number=a['number'],
            defaults={
                'chapter':    chapters[c_key],
                'title_en':   a['title_en'],
                'content_en': a['content_en'],
                'content_fr': a['content_fr'],
                'content_rw': a['content_rw'],
            }
        )
        print(f"      Article {a['number']}: {a['title_en'][:50]}")

    print(f"\n✓ Done! {Article.objects.count()} articles imported.")

if __name__ == '__main__':
    run()
