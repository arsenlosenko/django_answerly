from datetime import date

from django.test import TestCase, RequestFactory
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium.webdriver.chrome.webdriver import WebDriver

from qanda.factories import QuestionFactory
from qanda.models import Question
from qanda.views import DailyQuestionListView, SearchView
from user.factories import UserFactory

QUESTION_CREATED_STRFTIME = "%Y-%m-%d %H:%M"

# test create answer
# test create question


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


class TestQuestionDetailView(TestCase):
    QUESTION_DETAIL_SNIPPET = """
    <div class="question">
        <div class="meta col-sm-12">
            <h1>{title}</h1>
            Asked by {user} on {date}
        </div>
        <div class="body col-sm-12">
            <p>{body}</p>
        </div>
    </div>
    """
    NO_ANSWERS_SNIPPET = """
        <li class="answer">No answers yet!</li>
    """
    LOGIN_TO_POST_ANSWERS = 'Login to post answers'

    def test_logged_in_user_can_post_answers(self):
        question = QuestionFactory()

        self.assertTrue(self.client.login(
            username=question.user.username,
            password=UserFactory.password
        ))
        response = self.client.get('/q/{}'.format(question.id))
        rendered_content = response.rendered_content
        self.assertEqual(200, response.status_code)
        self.assertInHTML(self.NO_ANSWERS_SNIPPET, rendered_content)

        template_names = [t.name for t in response.templates]
        self.assertIn('qanda/common/post_answer.html', template_names)

        question_needle = self.QUESTION_DETAIL_SNIPPET.format(
            title=question.title,
            user=question.user.username,
            date=question.created.strftime(QUESTION_CREATED_STRFTIME),
            body=QuestionFactory.question)
        self.assertInHTML(question_needle, rendered_content)


class TestAskQuestionForm(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver(executable_path=settings.CHROMEDRIVER)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = UserFactory()

    def test_can_ask_blank_questions(self):
        initial_questions_count = Question.objects.count()
        self.selenium.get('%s%s' % (self.live_server_url, '/user/login'))

        username_input = self.selenium.find_element_by_name('username')
        username_input.send_keys(self.user.username)
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(UserFactory.password)
        password_input.submit()

        self.selenium.find_element_by_link_text('Ask').click()
        ask_question_url = self.selenium.current_url
        question_textarea = self.selenium.find_element_by_id('id_question')
        question_textarea.submit()
        after_empty_submit_click = self.selenium.current_url

        self.assertEqual(ask_question_url, after_empty_submit_click)
        self.assertEqual(initial_questions_count, Question.objects.count())


class TestSearch(TestCase):
    SEARCH_RESULT_SNIPPET = """
        <li>
            <a href="/q/{id}">{title}</a>
            <div>
                <p>{body}</p>
            </div>
        </li>
    """

    def setUp(self):
        self.title = "test question"
        self.request = RequestFactory().get("/q/search", {"q": self.title})

    def test_search_query(self):
        question = QuestionFactory(
            title=self.title
        )
        response = SearchView.as_view()(self.request)
        self.assertEqual(200, response.status_code)

        rendered_content = response.rendered_content
        needle = self.SEARCH_RESULT_SNIPPET.format(
            id=question.id,
            title=question.title,
            body=question.question
        )
        self.assertInHTML(needle, rendered_content)
