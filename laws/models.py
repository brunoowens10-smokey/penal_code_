from django.db import models

class Title(models.Model):
    number = models.CharField(max_length=20)
    name_en = models.TextField()
    name_fr = models.TextField(blank=True)
    name_rw = models.TextField(blank=True)

    def __str__(self):
        return f"Title {self.number}: {self.name_en}"

class Chapter(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name='chapters')
    number = models.CharField(max_length=20)
    name_en = models.TextField()
    name_fr = models.TextField(blank=True)
    name_rw = models.TextField(blank=True)

    def __str__(self):
        return f"Chapter {self.number}: {self.name_en}"

class Article(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    number = models.CharField(max_length=20)
    title_en = models.CharField(max_length=300, blank=True)
    content_en = models.TextField()
    content_fr = models.TextField(blank=True)
    content_rw = models.TextField(blank=True)

    def __str__(self):
        return f"Article {self.number}: {self.title_en}"