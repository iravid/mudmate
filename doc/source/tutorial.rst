.. _tutorial_toplevel:

========================
A Quick MudMate Tutorial
========================

Alright, so let's get down and dirty. Here's the example:

.. sourcecode:: python

   class ControlServerFactory(Factory, Subscriber):
       def __init__(self):
           self.mainConnection = None

           EventBus.instance.subscribe(self)
