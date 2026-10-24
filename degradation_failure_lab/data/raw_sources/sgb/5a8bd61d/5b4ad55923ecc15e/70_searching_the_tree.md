# Searching the tree

Beautiful Soup defines a lot of methods for searching the parse tree,
but they're all very similar. I'm going to spend a lot of time explaining
the two most popular methods: `find()` and `find_all()`. The other
methods take almost exactly the same arguments, so I'll just cover
them briefly.

Once again, I'll be using the "three sisters" document as an example:

```python
html_doc = """
The Dormouse's story

**The Dormouse's story**

Once upon a time there were three little sisters; and their names were
[Elsie](http://example.com/elsie),
[Lacie](http://example.com/lacie) and
[Tillie](http://example.com/tillie);
and they lived at the bottom of a well.

...

"""

from bs4 import BeautifulSoup
soup = BeautifulSoup(html_doc, 'html.parser')
```

By passing in a filter to a method like `find_all()`, you can
zoom in on the parts of the document you're interested in.

## Kinds of filters

Before talking in detail about `find_all()` and similar methods, I
want to show examples of different filters you can pass into these
methods. These filters show up again and again, throughout the
search API. You can use them to filter based on a tag's name,
on its attributes, on the text of a string, or on some combination of
these.

### A string

The simplest filter is a string. Pass a string to a search method and
Beautiful Soup will perform a tag-name match against that exact string.
This code finds all the <b> tags in the document:

```python
soup.find_all('b')
