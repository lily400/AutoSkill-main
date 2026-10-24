# match_template and pad_input

This task checks the documented difference between `pad_input=False` and `pad_input=True`.

- Without padding, the result shape shrinks relative to the template size.
- With padding, the response map aligns with the original image coordinates.
- The peak coordinate can therefore shift interpretation between top-left alignment and centered alignment.
