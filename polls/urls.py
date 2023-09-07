from django.urls import path
from . import views
from .views import (
    polls_view,
    poll_tags,
    poll_question_id,
    poll_giventag,
    create_question,
    poll_updatevote,
)


urlpatterns = [
    path("api/polls/", polls_view),
    path("api/polls_tags/", poll_tags),
    path("api/getpolls/<int:question_id>/", poll_question_id),
    # path("api/polls/poll_giventag?tag_value=<tag_value>", views.poll_giventag),
    # path("api/tagpolls/<str:tag_value>", poll_giventag),
    # path("api/tagpolls/?tags=<str:tag_value>/", poll_giventag),
    path("api/polls/poll_giventag", views.poll_giventag, name="poll_giventag"),
    path("api/question/", create_question),
    path("api/updatepolls/<int:question_id>/", poll_updatevote),
]
