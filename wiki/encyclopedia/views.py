import re
from random import choice

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util
from .forms import createForm


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def show_entry(request, entry):
	article = util.parse_entry(entry)
	if article is None:
		message = f"Sorry, entry '{entry.capitalize()}' was not found."
		return render(request, "encyclopedia/index.html", {
			"entries": util.list_entries(),
			"messages": [message],
			"mtype": "danger"
		})
	return render(request, "encyclopedia/article.html", {
		"title": entry,
		"article": article,
		"messages": ["Article was successfully loaded"],
		"mtype": "success"
	})
	
def search_result(request):
	query = request.GET["q"]
	if not query or re.match("^\s+$", query):
		return HttpResponseRedirect(reverse('encyclopedia:index'))
	query.lstrip().rstrip()
	entries = util.list_entries()
	if query in entries:
		return HttpResponseRedirect(reverse('encyclopedia:show_entry', args=(
			query,
		)))
	pattern = "(?i)"+query
	title_matches = [entry for entry in entries if re.search(pattern, entry)]
	text_matches = []
	for entry in entries:
		if entry not in title_matches:
			content = util.get_entry(entry)
			queryMatch = re.search(pattern, content)
			if queryMatch:
				text_matches.append([entry, "..."+content[
				(0 if queryMatch.start()-20 < 0 else queryMatch.start()-20): \
				queryMatch.start()], content[queryMatch.start():queryMatch.end()+1],
				content[queryMatch.end()+1:(len(content) if queryMatch.end()+20>= \
				len(content) else queryMatch.end()+20)]+"..."])
	if title_matches == [] and text_matches == []:
		message = "No entry found. Please amend your search criteria and try again."
		return render(request, "encyclopedia/index.html",
			{"entries": entries,
			"messages": [message],
			"mtype": "danger"}
		)
	message = f"Total of {len(title_matches) + len(text_matches)} results was found"
	return render(request, "encyclopedia/search.html", {
		"in_titles": title_matches,
		"in_content": text_matches,
		"messages": [message],
		"mtype": "success"
	})
	
def create_page(request):
	if request.method == "POST":
		
		form = createForm(request.POST)
		
		if form.is_valid():
			title = form.cleaned_data["title"]
			ftype = form.cleaned_data["ftype"]
			if title in util.list_entries() and ftype == "new":
				message = f"Article with the name \"{title}\" already exists."
				return render(request, "encyclopedia/create.html", {
					"pageTitle": "Create new article",
					"createForm": form,
					"messages": [message],
					"mtype": "danger"
				})
			content = form.cleaned_data["content"]
			
			try:
				util.save_entry(title, content)
			except:
				message = f"Error. Can not save article"
				return render(request, "encyclopedia/create.html", {
					"createForm": form,
					"messages": [message],
					"mtype": "danger"
				})
			return HttpResponseRedirect(reverse('encyclopedia:show_entry', args=(
											title,
										)))
	form = createForm()
	return render(request, "encyclopedia/create.html", {
		"pageTitle": "Create new article",
		"createForm": form
	})

def edit_page(request, entry):
	article = util.get_entry(entry)
	form = createForm(initial={"ftype": "edit", "title": entry, "content": article})
	return render(request, "encyclopedia/create.html", {
		"pageTitle": "Edit article",
		"createForm": form
	})

def show_random(request):
	entries = util.list_entries()
	return HttpResponseRedirect(reverse('encyclopedia:show_entry', args=(
											choice(entries),
										)))		
