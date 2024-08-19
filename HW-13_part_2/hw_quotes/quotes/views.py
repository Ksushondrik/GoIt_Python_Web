from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quote, Author, Tag
from .forms import AuthorForm, QuoteForm


# Create your views here.


def main(request, page=1):
    quotes = Quote.objects.all()
    per_page = 5
    paginator = Paginator(list(quotes), per_page)
    quotes_on_page = paginator.page(page)
    context = {'quotes': quotes_on_page}
    return render(request, 'quotes/index.html', context)


def author_detail(request, author_name):
    author = get_object_or_404(Author, fullname=author_name)
    try:
        # Спробуйте конвертувати born_date в об'єкт datetime
        born_date_formatted = datetime.strptime(author.born_date, "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y")
    except ValueError:
        born_date_formatted = author.born_date  # Якщо формат не відповідає, відображайте як є

    context = {'author': author, 'born_date_formatted': born_date_formatted}
    return render(request, 'quotes/author_detail.html', context)


def tag_detail(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    quotes = Quote.objects.filter(tags=tag)
    context = {'tag': tag, 'quotes': quotes}
    return render(request, 'quotes/tag_detail.html', context)


@login_required
def add_author(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            # Отримання значення fullname
            fullname = form.cleaned_data['fullname']

            # Перевірка, чи вже існує автор з таким fullname
            if Author.objects.filter(fullname=fullname).exists():
                messages.error(request, 'Author with this name already exists.')
            else:
                form.save()
                messages.success(request, 'Author added successfully.')
                return redirect('quotes:root')  # або інший маршрут за вашим вибором
    else:
        form = AuthorForm()
    return render(request, 'quotes/add_author.html', {'form': form})


@login_required
def add_quote(request):
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quote added successfully.')
            return redirect('quotes:root')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuoteForm()
    return render(request, 'quotes/add_quote.html', {'form': form})
