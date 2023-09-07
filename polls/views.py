from django.template import loader
from django.shortcuts import get_object_or_404, render
from .models import Question
from django.http import Http404
from django.shortcuts import render
from .models import Question
from django.http import HttpResponse, HttpResponseRedirect
from .models import Choice, Question
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Question, Tags
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone


# GET viewing all polls
@csrf_exempt
def polls_view(request):
    questions = Question.objects.all()
    data = []
    for question in questions:
        choices = Choice.objects.filter(question=question)
        tags = Tags.objects.filter(question=question)
        choice_dict = {choice.choice_text: choice.votes for choice in choices}
        total_votes = sum(choice.votes for choice in choices)
        question_data = {
            "Question": question.question_text,
            "OptionVote": choice_dict,
            "Tags": [tag.tags_text for tag in tags],
            "TotalVotes": total_votes,
            "QuestionId": question.id,
        }
        data.append(question_data)
    return JsonResponse(data, safe=False)


# GET /polls/tags/
@csrf_exempt
def poll_tags(request):
    tags = Tags.objects.all()
    data = []
    question_data = {"tags": [tag.tags_text for tag in tags]}
    data.append(question_data)
    return JsonResponse(data, safe=False)


# GET/polls/question_id
@csrf_exempt
def poll_question_id(request, question_id):
    if request.method == "GET":
        try:
            question = Question.objects.get(pk=question_id)
            print("question",question)
            choices = Choice.objects.filter(question=question)
            print("choices",choices)
            tags = Tags.objects.filter(question=question)
            print("tags", tags)
            choice_dict = {choice.choice_text: choice.votes for choice in choices}
            data = {
                "Question": question.question_text,
                "OptionVote": choice_dict,
                "Tags": [tag.tags_text for tag in tags],
            }

            return JsonResponse(data)
        except Question.DoesNotExist:
            return JsonResponse({"error": "Question does not exist"}, status=404)


# GET/polls/polls_giventag
@csrf_exempt
def poll_giventag(request):
    tag_values = request.GET.get("tag_value").split(",")
    print("tag_values=", tag_values)
    # tags = Tags.objects.filter(tags_text=tag_values)
    tags = Tags.objects.filter(tags_text__in=tag_values)
    print("tags", tags)

    questions = Question.objects.all()
    data = []
    for question in questions:
        choices = Choice.objects.filter(question=question)
        total_votes = sum(choice.votes for choice in choices)

        # tags = Tags.objects.filter(question=question)
        matching_tags = Tags.objects.filter(question=question, tags_text__in=tag_values)
        all_tags = Tags.objects.filter(question=question).values_list(
            "tags_text", flat=True
        )

        if matching_tags:
            tags = [tag.tags_text for tag in matching_tags]
            print("tags=", tags)
            other_tags = [
                tag
                for tag in all_tags
                if tag not in matching_tags.values_list("tags_text", flat=True)
            ]
            print("other_tags=", other_tags)
            data.append(
                {
                    "Question": question.question_text,
                    "OptionVote": [
                        {"Option": choice.choice_text, "votes": choice.votes}
                        for choice in choices
                    ],
                    "TotalVotes": total_votes,
                    "Tags": tags + other_tags,
                    "QuestionId": question.id,
                }
            )
    if data:
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse(
            {"error": "No questions found with the given tags"}, status=404
        )


@csrf_exempt
# POST/polls/create_question
def create_question(request):
    if request.method == "POST":
        print("hello")
        payload = json.loads(request.body.decode("utf-8"))
        question_text = payload.get("Question")
        option_votes = payload.get("OptionVote", {})
        tags = payload.get("Tags", [])
        # question_text = payload.get("Question")
        print("q", question_text)
        # option_votes = payload.get("OptionVote", {})
        # tags = payload.get("Tags", [])
        print(question_text)
        print(option_votes)
        print(tags)
        if question_text and option_votes:
            payload = json.loads(request.body.decode("utf-8"))
            question = Question(question_text=question_text, pub_date=timezone.now())
            question.save()

        for choice_text, votes in option_votes.items():
            choice = Choice(
                question=question, choice_text=choice_text, votes=int(votes)
            )
            choice.save()

        for tag in tags:
            tag_obj = Tags(question=question, tags_text=tag)
            tag_obj.save()

        return JsonResponse({"message": "Question added successfully."})
    else:
        return JsonResponse({"error": "Invalid data provided."}, status=400)


@csrf_exempt
# PUT/polls/question_id
def poll_updatevote(request, question_id):
    if request.method == "PUT":
        print("question_id ", question_id)

        print("hello")
        try:
            print("question_id ", question_id)
            data = json.loads(request.body)
            print("data", data)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)

        try:
            question = Question.objects.get(pk=question_id)
            print("Ques", question)
        except Question.DoesNotExist:
            return JsonResponse({"error": "Question does not exist."}, status=404)
        choices = Choice.objects.filter(question=question_id)
        print("choice1", choices)
        increment_option = data.get("incrementoption")
        print("increment_option", increment_option)
        if increment_option:
            try:
                choice = Choice.objects.get(
                    question=question, choice_text=increment_option
                )
                choice.votes += 1
                choice.save()
                return JsonResponse({"message": "Vote incremented successfully."})
            except Choice.DoesNotExist:
                return JsonResponse(
                    {"error": "Choice does not exist for the given question."},
                    status=404,
                )
        else:
            return JsonResponse({"error": "Invalid data provided."}, status=400)


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/details.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    ...  # same as above, no changes needed.


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/results.html", {"question": question})


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})


def index(request):
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_question_list": latest_question_list}
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
