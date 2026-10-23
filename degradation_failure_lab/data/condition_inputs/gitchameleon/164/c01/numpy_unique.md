# NumPy 1.25.1 official API documentation

## numpy.unique

```python
def unique(ar, return_index=False, return_inverse=False,
           return_counts=False, axis=None, *, equal_nan=True):
```

Find the unique elements of an array.

Returns the sorted unique elements of an array. There are three optional
outputs in addition to the unique elements:

* the indices of the input array that give the unique values
* the indices of the unique array that reconstruct the input array
* the number of times each unique value comes up in the input array

Parameters
----------
ar : array_like
    Input array. Unless `axis` is specified, this will be flattened if it
    is not already 1-D.
return_index : bool, optional
    If True, also return the indices of `ar` (along the specified axis,
    if provided, or in the flattened array) that result in the unique array.
return_inverse : bool, optional
    If True, also return the indices of the unique array (for the specified
    axis, if provided) that can be used to reconstruct `ar`.
return_counts : bool, optional
    If True, also return the number of times each unique item appears
    in `ar`.
axis : int or None, optional
    The axis to operate on. If None, `ar` will be flattened. If an integer,
    the subarrays indexed by the given axis will be flattened and treated
    as the elements of a 1-D array with the dimension of the given axis,
    see the notes for more details.  Object arrays or structured arrays
    that contain objects are not supported if the `axis` kwarg is used. The
    default is None.

    .. versionadded:: 1.13.0

Returns
-------
unique : ndarray
    The sorted unique values.
unique_indices : ndarray, optional
    The indices of the first occurrences of the unique values in the
    original array. Only provided if `return_index` is True.
unique_inverse : ndarray, optional
    The indices to reconstruct the original array from the
    unique array. Only provided if `return_inverse` is True.
unique_counts : ndarray, optional
    The number of times each of the unique values comes up in the
    original array. Only provided if `return_counts` is True.

    .. versionadded:: 1.9.0

See Also
--------
numpy.lib.arraysetops : Module with a number of other functions for
                        performing set operations on arrays.
repeat : Repeat elements of an array.

Notes
-----
When an axis is specified the subarrays indexed by the axis are sorted.
This is done by making the specified axis the first dimension of the array
(move the axis to the first dimension to keep the order of the other axes)
and then flattening the subarrays in C order. The flattened subarrays are
then viewed as a structured type with each element given a label, with the
effect that we end up with a 1-D array of structured types that can be
treated in the same way as any other 1-D array. The result is that the
flattened subarrays are sorted in lexicographic order starting with the
first element.

.. versionchanged: NumPy 1.21
    If nan values are in the input array, a single nan is put
    to the end of the sorted unique values.

    Also for complex arrays all NaN values are considered equivalent
    (no matter whether the NaN is in the real or imaginary part).
    As the representant for the returned array the smallest one in the
    lexicographical order is chosen - see np.sort for how the lexicographical
    order is defined for complex arrays.

Examples
--------
>>> np.unique([1, 1, 2, 2, 3, 3])
array([1, 2, 3])
>>> a = np.array([[1, 1], [2, 3]])
>>> np.unique(a)
array([1, 2, 3])

Return the unique rows of a 2D array

>>> a = np.array([[1, 0, 0], [1, 0, 0], [2, 3, 4]])
>>> np.unique(a, axis=0)
array([[1, 0, 0], [2, 3, 4]])

Return the indices of the original array that give the unique values:

>>> a = np.array(['a', 'b', 'b', 'c', 'a'])
>>> u, indices = np.unique(a, return_index=True)
>>> u
array(['a', 'b', 'c'], dtype='<U1')
>>> indices
array([0, 1, 3])
>>> a[indices]
array(['a', 'b', 'c'], dtype='<U1')

Reconstruct the input array from the unique values and inverse:

>>> a = np.array([1, 2, 6, 4, 2, 3, 2])
>>> u, indices = np.unique(a, return_inverse=True)
>>> u
array([1, 2, 3, 4, 6])
>>> indices
array([0, 1, 4, 3, 1, 2, 1])
>>> u[indices]
array([1, 2, 6, 4, 2, 3, 2])

Reconstruct the input values from the unique values and counts:

>>> a = np.array([1, 2, 6, 4, 2, 3, 2])
>>> values, counts = np.unique(a, return_counts=True)
>>> values
array([1, 2, 3, 4, 6])
>>> counts
array([1, 3, 1, 1, 1])
>>> np.repeat(values, counts)
array([1, 2, 2, 2, 3, 4, 6])    # original order not preserved

## numpy.ndarray.tolist

a.tolist()

Return the array as an ``a.ndim``-levels deep nested list of Python scalars.

Return a copy of the array data as a (nested) Python list.
Data items are converted to the nearest compatible builtin Python type, via
the `~numpy.ndarray.item` function.

If ``a.ndim`` is 0, then since the depth of the nested list is 0, it will
not be a list at all, but a simple Python scalar.

Parameters
----------
none

Returns
-------
y : object, or list of object, or list of list of object, or ...
    The possibly nested list of array elements.

Notes
-----
The array may be recreated via ``a = np.array(a.tolist())``, although this
may sometimes lose precision.

Examples
--------
For a 1D array, ``a.tolist()`` is almost the same as ``list(a)``,
except that ``tolist`` changes numpy scalars to Python scalars:

>>> a = np.uint32([1, 2])
>>> a_list = list(a)
>>> a_list
[1, 2]
>>> type(a_list[0])
<class 'numpy.uint32'>
>>> a_tolist = a.tolist()
>>> a_tolist
[1, 2]
>>> type(a_tolist[0])
<class 'int'>

Additionally, for a 2D array, ``tolist`` applies recursively:

>>> a = np.array([[1, 2], [3, 4]])
>>> list(a)
[array([1, 2]), array([3, 4])]
>>> a.tolist()
[[1, 2], [3, 4]]

The base case for this recursion is a 0D array:

>>> a = np.array(1)
>>> list(a)
Traceback (most recent call last):
  ...
TypeError: iteration over a 0-d array
>>> a.tolist()
1

