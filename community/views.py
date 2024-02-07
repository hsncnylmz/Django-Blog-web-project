# community/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Question, Answer
from .forms import QuestionForm, AnswerForm
from paper.models import Paper
from blog.models import Blog, Tag

def question_detail(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        tags = Tag.objects.all()
        latest_post = Blog.objects.filter(is_active=True, is_home=True).order_by('-publish_date').first()
    except Question.DoesNotExist:
        return render(request, 'community/soru_bulunamadi.html')

    answers = question.answers.all()

    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.user = request.user
            answer.save()
            return redirect('community:question_detail', question_id=question_id)

    else:
        form = AnswerForm()

    return render(request, 'community/question_detail.html', {
        'question': question, 
        'answers': answers, 
        'form': form,
        'latest_post': latest_post,
        'all_tags': Tag.objects.all(),
    })

def question_list(request):
    questions = Question.objects.all().order_by('-created_at')
    question_form = QuestionForm()
    tags = Tag.objects.all()
    latest_post = Blog.objects.filter(is_active=True, is_home=True).order_by('-publish_date').first()

    # Önceki soruların listesi
    previous_questions = Question.objects.exclude(id__in=questions.values_list('id', flat=True))
    
    if request.method == 'POST':
        if 'ask_question' in request.POST:
            question_form = QuestionForm(request.POST, request.FILES)
            if question_form.is_valid():
                question = question_form.save(commit=False)
                question.user = request.user
                question.save()
                return redirect('community:question_list')

    return render(request, 'community/question_list.html', {
        'questions': questions,
        'question_form': question_form,
        'previous_questions': previous_questions,
        'latest_post': latest_post,
        'all_tags': Tag.objects.all(),
    })


def ask_question(request):
    # Önceki soruların listesi
    previous_questions = Question.objects.all().order_by('-created_at')

    # En son eklenen makalelerin listesi
    latest_papers = Paper.objects.all().order_by('-publish_date')[:5]  # Assuming publish_date is a valid field
    tags = Tag.objects.all()
    latest_post = Blog.objects.filter(is_active=True, is_home=True).order_by('-publish_date').first()

    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            return redirect('community:question_list')
    else:
        form = QuestionForm()

    return render(request, 'community/ask_question.html', {
        'form': form,
        'previous_questions': previous_questions,
        'latest_papers': latest_papers,
        'latest_post': latest_post,
        'all_tags': Tag.objects.all(),
    })

@login_required
def answer_question(request, question_id):
    question = Question.objects.get(pk=question_id)
    tags = Tag.objects.all()
    latest_post = Blog.objects.filter(is_active=True, is_home=True).order_by('-publish_date').first()
    
    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.user = request.user
            answer.save()
            return redirect('community:question_detail', question_id=question.id)
    else:
        form = AnswerForm()

    return render(request, 'community/answer_question.html', {
        'form': form, 
        'question': question,
        'latest_post': latest_post,
        'all_tags': Tag.objects.all(),
    })

@login_required
def edit_question(request, question_id):
    try:
        question = Question.objects.get(pk=question_id, user=request.user)
    except Question.DoesNotExist:
        # Eğer obje bulunamazsa istediğiniz bir işlemi yapabilirsiniz.
        # Örneğin, basit bir mesaj göstermek:
        return render(request, 'community/soru_bulunamadi.html')

    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            form.save()
            return redirect('community:question_detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'community/edit_question.html', {'form': form, 'question': question})

@login_required
def delete_question(request, question_id):
    try:
        question = Question.objects.get(pk=question_id, user=request.user)
    except Question.DoesNotExist:
        # Eğer obje bulunamazsa istediğiniz bir işlemi yapabilirsiniz.
        # Örneğin, basit bir mesaj göstermek:
        return render(request, 'community/soru_bulunamadi.html')

    if request.method == 'POST':
        question.delete()
        return redirect('community:question_list')

    return render(request, 'community/delete_question.html', {'question': question})

@login_required
def delete_answer(request, answer_id):
    try:
        answer = Answer.objects.get(pk=answer_id, user=request.user)
        # Yukarıdaki satırda Answer modeline özgü olarak user filtresi eklenmiştir.
        # Eğer Answer modelinde user alanı yoksa, bu filtre eklenmemelidir.
    except Answer.DoesNotExist:
        # Eğer obje bulunamazsa istediğiniz bir işlemi yapabilirsiniz.
        # Örneğin, basit bir mesaj göstermek:
        return render(request, 'community/soru_bulunamadi.html')

    if request.method == 'POST':
        answer.delete()
        return redirect('community:question_list')  # veya başka bir sayfaya yönlendirme yapabilirsiniz

    return render(request, 'community/delete_answer.html', {'answer': answer})