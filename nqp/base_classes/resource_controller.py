import weakref
from typing import Callable


class ResourceController:
    """
    Base class with a general specification for lazily loading game resources.

    Resources in a ResourceController can be accessed just like in a dictionary.
    """

    def __init__(self, loader: Callable, is_weakref: bool):
        """
        Initialize a ResourceController.

        :param loader: function used to create a new object. When it does not exist,
        the loader function gets called with the key passed to the controller as an
        argument.
        :param is_weakref: weakref is used to allow garbage collecting values that are no longer used
        even if they are referenced by the dictionary, meaning the cache dictionary
        does not increase the reference count for its values, so they get can be
        released from memory when not referenced elsewhere.
        """
        self.cache = weakref.WeakValueDictionary() if is_weakref else dict()
        self.loader = loader

    def __setitem__(self, name, value):
        """
        Set value for a name in the dictionary
        :param name: the key that's getting its value set
        :param value: the new value for it
        """
        self.cache[name] = value

    def __getitem__(self, name):
        """
        Get items from a ResourceController like it's a dictionary
        :param name: the key used to access a resource
        :return: the item already in cache or the item that didn't exist and was loaded
        """
        try:
            img = self.cache[name]
        except KeyError:
            img = self.loader(name)
            self.cache[name] = img

        return img
