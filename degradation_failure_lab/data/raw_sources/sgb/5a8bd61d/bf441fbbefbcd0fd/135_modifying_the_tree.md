# Modifying the tree

Beautiful Soup's main strength is in searching the parse tree, but you
can also modify the tree and write your changes as a new HTML or XML
document.

## Changing tag names and attributes

I covered this earlier, in [`Tag.attrs`](#Tag.attrs), but it bears repeating. You
can rename a tag, change the values of its attributes, add new
attributes, and delete attributes:

```python
soup = BeautifulSoup('**Extremely bold**', 'html.parser')
tag = soup.b

tag.name = "blockquote"
tag['class'] = 'verybold'
tag['id'] = 1
tag
