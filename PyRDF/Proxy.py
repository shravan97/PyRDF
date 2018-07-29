from __future__ import print_function
from .CallableGenerator import CallableGenerator

class Proxy(object):
    """
    This class wraps action nodes and instances of Proxy act as
    futures of the result produced by some action. They implement
    a lazy synchronization mechanism, i.e., when they are accessed
    for the first time, they trigger the execution of the whole
    RDataFrame graph.

    Attributes
    ----------
    backend
        A class member to store a backend object
        based on the configuration set by the user.

    action_node
        The action node that the current Proxy
        instance wraps.

    """
    def __init__(self, action_node):
        """
        Creates a new `Proxy` object for a
        given action node.

        Parameters
        ----------
        action_node : PyRDF.Node
            The action node that the current Proxy
            should wrap.

        """
        self.action_node = action_node

    def __eq__(self, obj):
        """
        Checks if the given object is equal to
        the value of the current action node.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value to which the current action node's
            value is compared.

        """
        self._check_and_execute()
        # Checking both ways is required because there is no reverse
        # equal dunder like '__req__'.
        return (self.action_node.value == obj) or (obj == self.action_node.value)

    def __add__(self, obj):
        """
        Adds the input object with current
        action node's value.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value to which the current action node's
            value is added.

        """
        self._check_and_execute()
        return self.action_node.value + obj

    def __radd__(self, obj):
        """
        Adds the input object with current
        action node's value.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value to which the current action node's
            value is added.

        """
        self._check_and_execute()
        return self.action_node.value + obj

    def __sub__(self, obj):
        """
        Subtracts the current action node's value
        from the input object.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            Current action node's value is subtracted
            from this value.

        """
        self._check_and_execute()
        return self.action_node.value - obj

    def __rsub__(self, obj):
        """
        Subtracts the the input object from current
        action node's value.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value from which the current action node's
            value is subtracted.

        """
        self._check_and_execute()
        return obj - self.action_node.value

    def __mul__(self, obj):
        """
        Multiplies the input object with current
        action node's value.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value to which the current action node's
            value is multiplied.

        """
        self._check_and_execute()
        return self.action_node.value * obj

    def __rmul__(self, obj):
        """
        Multiplies the input object with current
        action node's value.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value to which the current action node's
            value is multiplied.

        """
        self._check_and_execute()
        return self.action_node.value * obj

    def __div__(self, obj):
        """
        Divides the current action node's value
        by input object.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value which divides the current
            action node's value.

        """
        self._check_and_execute()
        return self.action_node.value/obj

    def __rdiv__(self, obj):
        """
        Divides the input object by current
        action node's value.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value by which the current action
            node's value is divided.

        """
        self._check_and_execute()
        return obj/self.action_node.value

    def __truediv__(self, obj):
        """
        Divides the current action node's value
        by input object. This method is specifically
        for division in Python3.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value which divides the current
            action node's value.

        """
        self._check_and_execute()
        return self.action_node.value/obj

    def __rtruediv__(self, obj):
        """
        Divides the input object by current
        action node's value. This method is specifically
        for division in Python3.

        Parameters
        ----------
        obj : numbers.Number or PyRDF.Proxy.Proxy
            The value by which the current action
            node's value is divided.

        """
        self._check_and_execute()
        return obj/self.action_node.value

    def __str__(self):
        """
        Returns the string representation
        of the current action node's value.

        """
        self._check_and_execute()
        return str(self.action_node.value)

    def __getattr__(self, attr):
        """
        Intercepts calls on the result of
        the action node.

        Returns
        -------
        function
            A method to handle an operation call to the
            current action node.

        """

        self._cur_attr = attr # Stores the name of operation call
        return self._call_handler
    
    def _check_and_execute(self):
        # Checks if execution of computation
        # got over and triggers the event-loop
        # if not over.

        if not self.action_node.value:
            from . import current_backend
            generator = CallableGenerator(self.action_node.get_head())
            current_backend.execute(generator)

    def _call_handler(self, *args, **kwargs):
        # Handles an operation call to the current action node
        # and returns result of the current action node.
        self._check_and_execute()

        return getattr(self.action_node.value, self._cur_attr)(*args, **kwargs)