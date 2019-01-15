from datetime import date

from django.test import TestCase, RequestFactory

from qanda.factories import QuestionFactory
from qanda.views import DailyQuestionListView

QUESTION_CREATED_STRFTIME = "%Y-%m-%d %H:%M"


class TestDailyQuestionListView(TestCase):
    QUESTION_LIST_NEEDLE_TEMPLATE = """
    <li>

        <a href="/q/{id}">{title}</a>
        by {username} on {date}
    </li>
    """

    REQUEST = RequestFactory().get(path="/q/2030-12-31")
    TODAY = date.today()

    def test_GET_on_day_with_many_questions(self):
        todays_questions = [QuestionFactory() for _ in range(10)]

        response = DailyQuestionListView.as_view()(
            self.REQUEST,
            year=self.TODAY.year,
            month=self.TODAY.month,
            day=self.TODAY.day
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(10, response.context_data['object_list'].count())
        rendered_content = response.rendered_content
        for question in todays_questions:
            needle = self.QUESTION_LIST_NEEDLE_TEMPLATE.format(
                id=question.id,
                title=question.title,
                username=question.user.username,
                date=question.created.strftime(QUESTION_CREATED_STRFTIME)
            )
            self.assertInHTML(needle, rendered_content)
