from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from . import util
from django import forms
from django.urls import reverse
from random import shuffle
import markdown2

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(), 
        'message': "All pages" 
    })

def show(request, title):
    entries = util.list_entries()
    content = util.get_entry(title) 
    if content != None :
        return render(request, "encyclopedia/show.html", {
        "title": title, 
        "content": markdown2.markdown(str(content))
        })
    else :
        return HttpResponse(f"Error : the requested page was not Found.")

def search(request):
    user_query = request.POST.get('user_query')
    entry = util.get_entry(user_query)
    titles_list = util.list_titles()
    if user_query in titles_list: 
        return render(request, "encyclopedia/show.html", {
            "title": user_query,
            "content": entry
        })
    else :  
        similar_titles = []
        for title in titles_list :
            if user_query in title :
                similar_titles.append(title)

        return render(request, "encyclopedia/index.html", {
            "message": "You're probably looking for...",
            "entries": similar_titles
        })

class AddEntryForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Content", widget=forms.Textarea())

def add(request):
    titles_list = util.list_titles()
    if request.method == "POST" :
        form = AddEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            
            if title in titles_list :
                return HttpResponse(f"Error : this entry already exists")
            else: 
                util.save_entry(title, content)
                return render(request, "encyclopedia/show.html", {
                    "title": title,
                    "content": content
                })
        else:
            return render(request, "encyclopedia/add.html", { 
                "form": form 
            })

    if request.method == "GET" :
        return render(request, "encyclopedia/add.html", { 
            "form": AddEntryForm() 
        })

def edit(request, title):
    old_title = title
    old_content = util.get_entry(title)
    if request.method == "POST" :
        if request.POST.get('title') :
            new_title = request.POST.get('title')
        else :
            new_title = old_title
        if request.POST.get('content') :
            new_content = request.POST.get('content')
        else :
            new_content = old_content
        util.save_entry(new_title, new_content)
        return render(request, "encyclopedia/show.html", {
            "title": new_title,
            "content": new_content
        })
    if request.method == "GET" :
        return render(request, "encyclopedia/edit.html", { 
            "title": old_title, 
            "content": old_content
        })

def random(request):
    titles = util.list_titles()
    #random_title = random.choice(titles)
    shuffle(titles)
    random_title = titles[3]
    random_content = util.get_entry(random_title)
    return render(request, "encyclopedia/show.html", {
        "title": random_title,
        "content": random_content, 
    })
