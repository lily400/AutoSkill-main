# Making the soup

To parse a document, pass it into the `BeautifulSoup`
constructor. You can pass in a string or an open filehandle:

```python
from bs4 import BeautifulSoup

with open("index.html") as fp:
    soup = BeautifulSoup(fp, 'html.parser')

soup = BeautifulSoup("a web page", 'html.parser')
```

First, the document is converted to Unicode, and HTML entities are
converted to Unicode characters:

```python
print(BeautifulSoup("Sacr&eacute; bleu!", "html.parser"))
