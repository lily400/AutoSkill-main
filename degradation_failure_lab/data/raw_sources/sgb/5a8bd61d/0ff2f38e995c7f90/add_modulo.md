# Pillow ImageChops add and add_modulo

This task focuses on the difference between two Pillow image arithmetic helpers:

- `ImageChops.add()` performs clipped addition.
- `ImageChops.add_modulo()` performs modulo-256 addition.

When pixel values overflow beyond 255, the two functions diverge.
That is the main behavior under test.
