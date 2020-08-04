from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import forms
from django.db import models
import markdown2

from . import util

#creating forms

# form for creating entry
class TitleForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
    text = forms.CharField(label='Text', max_length=10000, widget=forms.Textarea)


class EditForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200,  widget=forms.TextInput(attrs={'readonly':'readonly'}))
    text = forms.CharField(label='Text', max_length=10000, widget=forms.Textarea)


#creating models

class Listing(models.Model):
    title = models.CharField(max_length=200)
    text = models.CharField(max_length=10000)



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, title):
    if util.get_entry(title) != None:
        return render(request, "encyclopedia/wiki.html", {
            "title": markdown2.markdown(util.get_entry(title)),
            "title_name": title
        })
    else:
        return render(request, "encyclopedia/doesnt_exist.html", {
            "title": util.get_entry(title),
            "title_name": title
        })


def search(request):
    if request.method == 'GET':
        query = request.GET.get("q", "")
        if util.get_entry(query) == None:
            # Creating list of entries
            list = util.list_entries()

            # Getting length of a list
            list_len = len(list)
            results = []

            for i in range(list_len):
                if query.lower() in list[i].lower():
                    results.append(list[i])
                    i += 1
                else:
                    i += 1
            print(results)
            if len(results) == 0:
                return render(request, "encyclopedia/doesnt_exist.html", {
                    "title": query,
                    "title_name": query
                })
            else:
                return render(request, "encyclopedia/index.html", {
                        "entries": results
                    })
        else:
            return wiki(request, query)
    else:
        return render(request, "encyclopedia/doesnt_exist.html")


def create(request):
    if request.method == 'GET':
        # if a GET we'll create a blank form
        form = TitleForm()

        return render(request, "encyclopedia/add_page.html", {
        'form': form
        })
        # if this is a POST request we need to process the form data
    elif request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TitleForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            obj = Listing() #gets new object
            obj.title = form.cleaned_data['title']
            obj.text = form.cleaned_data['text']
            
            #finally save the object in db

            if util.save_entry(obj.title, obj.text) == FileExistsError:
                return render (request, "encyclopedia/save_error.html", {
                    "title": obj.title
                })
            else:
                # redirect to a new URL:
                return wiki(request, obj.title)

        else:
            return render(request, 'index', {

            })
    else:
        return render(request, "encyclopedia/index.html", {
                "entries": results
            })


def edit(request, title):
    if request.method == 'GET':
        if util.get_entry(title) != None:
            # Calling the form with initial values prepopulated
            form = EditForm(initial={'title': title, 'text': util.get_entry(title)})

            return render(request, "encyclopedia/edit_page.html", {
                "form": form,
                "title": title
            })
        else:
            return render(request, "encyclopedia/error.html", {
                "title": util.get_entry(title),
                "title_name": title
            })
    elif request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EditForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            obj = Listing() #gets new object
            obj.title = title
            obj.text = form.cleaned_data['text']
            util.edit_entry(obj.title, obj.text)
            return wiki(request, obj.title)

def random(request):
    #calling random function from util
    title = util.random_item()
    return wiki(request, title)

   
