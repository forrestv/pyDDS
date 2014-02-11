pyDDS
=====

Python bindings to RTI's Data Distribution Service library

To use it, you must compile the DDS's generated code for message types into a shared
brary, and then load it with `dds.Library(path_to_so)`. Then, instantiate a
`dds.DDS()` object and call `.get_topic('topic_name', lib.TypeName)`
on it to get a `dds.Topic` object. The `Topic` object has blocking
`.send` and `.recv` methods, and you can set a callback with its
`.add_data_available_callback(func)` method.

See `test.py` for a (somewhat convoluted) example of blocking sending and receiving.

In addition, emulation of Twisted's protocol handling is provided by
`twisteddds.py`, with an example in `twistedds_example.py`.
