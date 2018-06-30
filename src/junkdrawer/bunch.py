from copy import deepcopy


class EqualityFromDict:
    """Mix-in allowing equality checking from instance's __dict__"""

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.__dict__ == other.__dict__


class ReprFromDict:
    """Mix-in implementing repr() from instance's __dict__"""

    def __repr__(self):
        state = ("{0:s}={1!r:s}".format(attribute, value) for (attribute, value) in self.__dict__.items())
        return "{0:s}.{1:s}({2:s})".format(self.__class__.__module__, self.__class__.__name__, ", ".join(state))


class Bunch(EqualityFromDict, ReprFromDict):
    """General purpose container.
    See http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52308
    """

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __contains__(self, key):
        return key in self.__dict__

    def __getitem__(self, key):
        return self.__dict__[key]

    def as_dict(self):
        return self.__dict__

    def __deepcopy__(self, memo):
        return Bunch(**deepcopy(self.as_dict()))
