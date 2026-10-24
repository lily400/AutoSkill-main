# Kinds of objects

Beautiful Soup transforms a complex HTML document into a complex tree
of Python objects. But you'll only ever have to deal with about four
*kinds* of objects: [`Tag`](#Tag), [`NavigableString`](#NavigableString), `BeautifulSoup`,
and [`Comment`](#Comment). These objects represent the HTML *elements*
that comprise the page.

*class *Tag(#Tag)

A [`Tag`](#Tag) object corresponds to an XML or HTML tag in the original document.

```python
soup = BeautifulSoup('**Extremely bold**', 'html.parser')
tag = soup.b
type(tag)
# 
```

Tags have a lot of attributes and methods, and I'll cover most of them
in [Navigating the tree](#navigating-the-tree) and [Searching the tree](#searching-the-tree). For now, the most
important methods of a tag are for accessing its name and attributes.

name(#Tag.name)

Every tag has a name:

```python
tag.name
