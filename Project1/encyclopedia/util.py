import re
import random

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


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
        return FileExistsError
        # default_storage.delete(filename) - old
    else:
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

def edit_entry(title, content):
    """
    Save edited  encyclopedia entry, given its title and Markdown
    content.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
        default_storage.save(filename, ContentFile(content))
    else:
        default_storage.save(filename, ContentFile(content))

def random_item():
    """
    Returns a random item from the list of all names of encyclopedia entries.
    """
    list = list_entries()
    max_length = len(list)
    rand_item = random.randint(0, max_length)
    random_entry = list[rand_item]

    return random_entry
