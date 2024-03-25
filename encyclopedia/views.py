from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from random import choice
import markdown2

from . import util


class NewPageForm(forms.Form):
    title = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Title", "style": "margin-bottom: 5px;"}
        ),
    )
    content = forms.CharField(
        label="", widget=forms.Textarea(attrs={"placeholder": "Markdown Content"})
    )


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def convert_md_to_html(title):
    if md := util.get_entry(title):
        return markdown2.markdown(md)
    return None


def entry(request, title):
    content = convert_md_to_html(title)
    return render(
        request,
        "encyclopedia/page.html",
        {"title": title.capitalize() if content else "Error", "content": content},
    )


def search(request):
    if request.method == "POST":
        title = request.POST.get("search_query")
        if util.get_entry(title):
            return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))
        results = []
        for entry in util.list_entries():
            if title.casefold() in entry.casefold():
                results.append(entry)

        return render(request, "encyclopedia/search.html", {"results": results})


def new_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if not util.get_entry(title):
                util.save_entry(title.capitalize(), content)
                return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))

            return render(
                request,
                "encyclopedia/new_page.html",
                {"form": NewPageForm(), "error": "This entry already exists!"},
            )

    return render(request, "encyclopedia/new_page.html", {"form": NewPageForm()})


def edit(request, title):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))

    content = util.get_entry(title)
    return render(
        request,
        "encyclopedia/new_page.html",
        {"form": NewPageForm({"title": title, "content": content})},
    )


def random(request):
    # entries = util.list_entries()
    # title = choice(entries)
    return HttpResponseRedirect(
        reverse("entry", kwargs={"title": choice(util.list_entries())})
    )
