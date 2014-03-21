from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    visits = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    # For prettified representation of a model instance
    # i.e. >> print Category will return <Category: Category object>
    # while __unicode__() will return <Category: given category's name>
    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name", "visits", "likes"]
        verbose_name_plural = "Categories"

class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ["category", "title", "url", "views"]
