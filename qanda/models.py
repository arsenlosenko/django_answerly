from django.conf import settings
from django.db import models
from django.urls.base import reverse
from django.contrib.postgres.search import SearchVector


class QuestionManager(models.Manager):
    def find_questions(self, query):
        qs = self.get_queryset()
        return qs.annotate(
            search=SearchVector('title', 'question')
        ).filter(search=query)


class Question(models.Model):
    title = models.CharField(max_length=140)
    question = models.TextField()
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    objects = QuestionManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("qanda:question-detail", kwargs=dict(pk=self.id))

    def can_accept_answers(self, user):
        return user == self.user


class Answer(models.Model):
    answer = models.TextField()
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(to=Question,
                                 on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created', )
