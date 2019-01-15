from django.urls import path

from qanda.views import (AskQuestionView, QuestionDetailView,
                         CreateAnswerView, UpdateAnswerAcceptanceView,
                         DailyQuestionListView, TodayQuestionListView)

app_name = 'qanda'
urlpatterns = [
    path('ask/',
         AskQuestionView.as_view(),
         name='ask'),

    path('q/<int:pk>',
         QuestionDetailView.as_view(),
         name="question-detail"),

    path('q/<int:pk>/answer',
         CreateAnswerView.as_view(),
         name="answer-question"),

    path('a/<int:pk>/accept',
         UpdateAnswerAcceptanceView.as_view(),
         name="update-answer-acceptance"),

    path('daily/<int:year>/<int:month>/<int:day>/',
         DailyQuestionListView.as_view(),
         name="daily-questions"),

    path('',
         TodayQuestionListView.as_view(),
         name="index")
]
