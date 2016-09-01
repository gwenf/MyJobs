=========
Overview
=========

MyBlocks was originally conceived as an idea to extend the customization of
Microsites webpages while offering a method for ease of reuse of components.
With MyBlocks, each block represents a bootstrap div with spans and offsets to
allow sizing of each module. Nesting of blocks can also occur, for instance: a
body block may contain a login block. These blocks may then combine with others
to create a entire dynamic webpage. The Login block contains special logic for
user login. Because of this, it is a subclass of Block rather than an instance
of Block.

.. autoclass:: myblocks.models.Page
.. autoclass:: myblocks.models.Block
.. autoclass:: myblocks.models.LoginBlock
