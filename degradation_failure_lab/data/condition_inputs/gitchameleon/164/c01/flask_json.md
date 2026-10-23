# Flask 3.0.0 official API documentation

## JSONProvider

```python
class JSONProvider:
```

A standard set of JSON operations for an application. Subclasses
of this can be used to customize JSON behavior or use different
JSON libraries.

To implement a provider for a specific library, subclass this base
class and implement at least :meth:`dumps` and :meth:`loads`. All
other methods have default implementations.

To use a different provider, either subclass ``Flask`` and set
:attr:`~flask.Flask.json_provider_class` to a provider class, or set
:attr:`app.json <flask.Flask.json>` to an instance of the class.

:param app: An application instance. This will be stored as a
    :class:`weakref.proxy` on the :attr:`_app` attribute.

.. versionadded:: 2.2

## JSONProvider.dumps

```python
    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
```

Serialize data as JSON.

:param obj: The data to serialize.
:param kwargs: May be passed to the underlying JSON library.

## JSONProvider.dump

```python
    def dump(self, obj: t.Any, fp: t.IO[str], **kwargs: t.Any) -> None:
```

Serialize data as JSON and write to a file.

:param obj: The data to serialize.
:param fp: A file opened for writing text. Should use the UTF-8
    encoding to be valid JSON.
:param kwargs: May be passed to the underlying JSON library.

## JSONProvider.loads

```python
    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any:
```

Deserialize data as JSON.

:param s: Text or UTF-8 bytes.
:param kwargs: May be passed to the underlying JSON library.

## JSONProvider.load

```python
    def load(self, fp: t.IO[t.AnyStr], **kwargs: t.Any) -> t.Any:
```

Deserialize data as JSON read from a file.

:param fp: A file opened for reading text or UTF-8 bytes.
:param kwargs: May be passed to the underlying JSON library.

## JSONProvider.response

```python
    def response(self, *args: t.Any, **kwargs: t.Any) -> Response:
```

Serialize the given arguments as JSON, and return a
:class:`~flask.Response` object with the ``application/json``
mimetype.

The :func:`~flask.json.jsonify` function calls this method for
the current application.

Either positional or keyword arguments can be given, not both.
If no arguments are given, ``None`` is serialized.

:param args: A single value to serialize, or multiple values to
    treat as a list to serialize.
:param kwargs: Treat as a dict to serialize.

## DefaultJSONProvider

```python
class DefaultJSONProvider(JSONProvider):
```

Provide JSON operations using Python's built-in :mod:`json`
library. Serializes the following additional data types:

-   :class:`datetime.datetime` and :class:`datetime.date` are
    serialized to :rfc:`822` strings. This is the same as the HTTP
    date format.
-   :class:`uuid.UUID` is serialized to a string.
-   :class:`dataclasses.dataclass` is passed to
    :func:`dataclasses.asdict`.
-   :class:`~markupsafe.Markup` (or any object with a ``__html__``
    method) will call the ``__html__`` method to get a string.

## DefaultJSONProvider.default

```python
default: t.Callable[[t.Any], t.Any]
```

Apply this function to any object that :meth:`json.dumps` does
not know how to serialize. It should return a valid JSON type or
raise a ``TypeError``.

## DefaultJSONProvider.ensure_ascii

```python
ensure_ascii = True
```

Replace non-ASCII characters with escape sequences. This may be
more compatible with some clients, but can be disabled for better
performance and size.

## DefaultJSONProvider.sort_keys

```python
sort_keys = True
```

Sort the keys in any serialized dicts. This may be useful for
some caching situations, but can be disabled for better performance.
When enabled, keys must all be strings, they are not converted
before sorting.

## DefaultJSONProvider.compact

```python
compact: bool | None = None
```

If ``True``, or ``None`` out of debug mode, the :meth:`response`
output will not add indentation, newlines, or spaces. If ``False``,
or ``None`` in debug mode, it will use a non-compact representation.

## DefaultJSONProvider.mimetype

```python
mimetype = "application/json"
```

The mimetype set in :meth:`response`.

## DefaultJSONProvider.dumps

```python
    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
```

Serialize data as JSON to a string.

Keyword arguments are passed to :func:`json.dumps`. Sets some
parameter defaults from the :attr:`default`,
:attr:`ensure_ascii`, and :attr:`sort_keys` attributes.

:param obj: The data to serialize.
:param kwargs: Passed to :func:`json.dumps`.

## DefaultJSONProvider.loads

```python
    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any:
```

Deserialize data as JSON from a string or bytes.

:param s: Text or UTF-8 bytes.
:param kwargs: Passed to :func:`json.loads`.

## DefaultJSONProvider.response

```python
    def response(self, *args: t.Any, **kwargs: t.Any) -> Response:
```

Serialize the given arguments as JSON, and return a
:class:`~flask.Response` object with it. The response mimetype
will be "application/json" and can be changed with
:attr:`mimetype`.

If :attr:`compact` is ``False`` or debug mode is enabled, the
output will be formatted to be easier to read.

Either positional or keyword arguments can be given, not both.
If no arguments are given, ``None`` is serialized.

:param args: A single value to serialize, or multiple values to
    treat as a list to serialize.
:param kwargs: Treat as a dict to serialize.

## App.json_provider_class

```python
json_provider_class: type[JSONProvider] = DefaultJSONProvider
```

A subclass of :class:`~flask.json.provider.JSONProvider`. An
instance is created and assigned to :attr:`app.json` when creating
the app.

The default, :class:`~flask.json.provider.DefaultJSONProvider`, uses
Python's built-in :mod:`json` library. A different provider can use
a different JSON library.

.. versionadded:: 2.2

## App.json

```python
self.json: JSONProvider
```

Provides access to JSON methods. Functions in ``flask.json``
will call methods on this provider when the application context
is active. Used for handling JSON requests and responses.

An instance of :attr:`json_provider_class`. Can be customized by
changing that attribute on a subclass, or by assigning to this
attribute afterwards.

The default, :class:`~flask.json.provider.DefaultJSONProvider`,
uses Python's built-in :mod:`json` library. A different provider
can use a different JSON library.

.. versionadded:: 2.2

## flask.json.jsonify

```python
def jsonify(*args: t.Any, **kwargs: t.Any) -> Response:
```

Serialize the given arguments as JSON, and return a
:class:`~flask.Response` object with the ``application/json``
mimetype. A dict or list returned from a view will be converted to a
JSON response automatically without needing to call this.

This requires an active request or application context, and calls
:meth:`app.json.response() <flask.json.provider.JSONProvider.response>`.

In debug mode, the output is formatted with indentation to make it
easier to read. This may also be controlled by the provider.

Either positional or keyword arguments can be given, not both.
If no arguments are given, ``None`` is serialized.

:param args: A single value to serialize, or multiple values to
    treat as a list to serialize.
:param kwargs: Treat as a dict to serialize.

.. versionchanged:: 2.2
    Calls ``current_app.json.response``, allowing an app to override
    the behavior.

.. versionchanged:: 2.0.2
    :class:`decimal.Decimal` is supported by converting to a string.

.. versionchanged:: 0.11
    Added support for serializing top-level arrays. This was a
    security risk in ancient browsers. See :ref:`security-json`.

.. versionadded:: 0.2

