from django.db import models
from django.contrib.auth.models import User

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
        verbose_name_plural = "Categories"

class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance
    user = models.OneToOneField(User)

    # The additional attributes we wish to include, apart from the default
    # provided (username, password, email, firstname, surname)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username
