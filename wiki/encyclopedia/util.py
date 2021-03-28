import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


patterns = [
	("#{6}\s+(.+)(?=\n|\Z)", r"<h6>\1</h6>"),
	("#{5}\s+(.+)(?=\n|\Z)", r"<h5>\1</h5>"),
	("#{4}\s+(.+)(?=\n|\Z)", r"<h4>\1</h4>"),
	("#{3}\s+(.+)(?=\n|\Z)", r"<h3>\1</h3>"),
	("#{2}\s+(.+)(?=\n|\Z)", r"<h2>\1</h2>"),
	("#\s+(.+)(?=\n|\Z)", r"<h1>\1</h1>"),
	("(\*{3})(\w+[\w\s$%&!?<>=-]*?\w{1})(\*{3})", 
		r"<span style='font-style: italic; font-weight: bold;'>\2</span>"),
	("(\*{2})(\w+[\w\s$%&!?<>=-]*?\w{1})(\*{2})", 
		r"<span style='font-weight: bold;'>\2</span>"),
	("(__)(\w+[\w\s$%&!?<>=-]*?\w{1})(__)", 
		r"<span style='font-weight: bold;'>\2</span>"),
	("(\*)(\w+[\w\s$%&!?<>=-]*?\w{1})(\*)",
		r"<span style='font-style: italic;'>\2</span>"),
	("(_)(\w+[\w\s$%&!?<>=-]*?\w{1})(_)", 
		r"<span style='font-style: italic;'>\2</span>"),
	("\[(.+?)\]\s*\((.+?)\)", r"<a href='\2'>\1</a>"),
	("(?m:^-(.+))(?=\n|\Z)", r"<ul><li>\1</li></ul>"),
	("(?m:^\*(.+))(?=\n|\Z)", r"<ul><li>\1</li></ul>"),
	("(?m:^(\d+)(\.)(?s:(.+?)))(?=(\n(?!(\d+\.)))|\Z)", 
		r"<ol start='\1'>\n\1\2\3\n</ol>"),
	("(?m:^(\d+\.)(.+))(?=\n|\Z)", r"<li>\2</li>"),
	("\n[\b\s]*\n(?P<par>[^<][^uo][^l][^>].+)(?=\n|\Z)", r"<p>\g<par></p>")
]


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None

def parse_entry(title):
	"""
	Calls util.get_entry(title). Processes retrieved encyclopedia
	entry to convert it from Markdown to HTML. Returns the entry
	as plain HTML. The following Markdown tags are supported:
	- headings
	- bold and italic text (and both simulteniously and nested)
	- unordered and ordered lists
	- links
	- paragraphs
	"""
	entry = get_entry(title)
	if not entry:
		return None
	for (markdown, html) in patterns:
		entry = re.sub(markdown, html, entry)
	return entry
	
