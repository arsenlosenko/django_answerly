import factory

from qanda.models import Question
from user.factories import UserFactory


class QuestionFactory(factory.DjangoModelFactory):
    title = factory.Sequence(lambda n: 'Question %s' % n)
    question = 'what is a question?'
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Question
