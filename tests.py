from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Question
from django.urls import reverse


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time=timezone.now() + datetime.timedelta(days=30)
        future_question=Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(),False)


    def test_was_published_recently_with_old_question(self):
        time=timezone.now()-datetime.timedelta(days=1, seconds=1)
        old_question=Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    time=timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(question, choice_text, votes):
    return question.choice_set.create(choice_text=choice_text, votes=votes)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        past_question = create_question(question_text="Past question.", days=-30)
        create_choice(past_question, 'choices', 0)
        response= self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question.>'])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        question = create_question(question_text="Future question.", days=30)
        create_choice(question, 'choices', 0)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        question = create_question(question_text="Past question.", days=-30)
        create_choice(question, 'choices', 0)
        question1 = create_question(question_text="Future question.", days=30)
        create_choice(question1, 'choices', 0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question.>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question=create_question(question_text="Past question 1.", days=-30)
        create_choice(question, 'choices', 0)
        question1=create_question(question_text="Past question 2.", days=-5)
        create_choice(question1, 'choices', 0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2.>', '<Question: Past question 1.>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        future_question = create_question(question_text='Future question.', days=5)
        create_choice(future_question, 'choices', 0)
        url = reverse('polls:details', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        past_question = create_question(question_text='Past Question.', days=-5)
        create_choice(past_question, 'choices', 0)
        url = reverse('polls:details', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionWithChoiceTests(TestCase):
    def test_with_choice(self):
        question=create_question(question_text='Question with choice.',days=-1)
        question.choice_set.create(choice_text='yes',votes=0)
        response=self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Question with choice.>'])

    def test_without_choice(self):
        question=create_question(question_text='Question without choice',days=-1)
        response=self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],[])