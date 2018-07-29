from PyRDF.Proxy import Proxy
from PyRDF.Node import Node
from PyRDF.backend.Backend import Backend
from PyRDF import RDataFrame
import unittest, PyRDF

class AttrReadTest(unittest.TestCase):
    """
    Test cases to check working of
    methods in Proxy class.

    """

    class Temp(object):
        """
        A mock action node result class.

        """
        def val(self, arg):
            """
            A test method to check function
            call on the Temp class.

            """
            return arg+123 # A simple operation to check

    def test_attr_simple(self):
        """
        Test case to check that a Proxy
        object reads the right input
        attribute.

        """

        node = Node(None, None)
        proxy = Proxy(node)
        func = proxy.attr

        self.assertEqual(proxy._cur_attr, "attr")

    def test_return_value(self):
        """
        Test case to check that a Proxy
        object computes and returns the
        right output based on the function call.

        """

        t = AttrReadTest.Temp()
        node = Node(None, None)
        node.value = t
        proxy = Proxy(node)

        self.assertEqual(proxy.val(21), 144)

class CheckAndExecuteTest(unittest.TestCase):
    """
    Tests to check the working of '_check_and_execute'
    method in Proxy class.

    """
    class TestBackend(Backend):
        """
        A Test implementation of Backend to check the
        working of '_check_and_execute' method in Proxy
        class.

        """
        def execute(self, generator):
            """
            Implementation of execute method for
            Test Backend.

            """
            # Record the head node for comparison
            self.obtained_head_node = generator.head_node

    def test_check_and_execute_with_proxy_value(self):
        """
        Test case to check the working of '_check_and_execute'
        method when the current action node's value is not None.

        """
        PyRDF.current_backend = CheckAndExecuteTest.TestBackend()

        action_node = Node(None, None)
        action_node.value = 10

        proxy = Proxy(action_node)
        proxy._check_and_execute()

        with self.assertRaises(AttributeError):
            # Ensure that execute was not called
            PyRDF.current_backend.obtained_head_node

    def test_check_and_execute_without_proxy_value(self):
        """
        Test case to check the working of '_check_and_execute'
        method when the current action node's value is None.

        """
        PyRDF.current_backend = CheckAndExecuteTest.TestBackend()

        rdf = RDataFrame(10)
        n1 = rdf.Define()
        n2 = n1.Count()

        n2._check_and_execute()

        self.assertIs(PyRDF.current_backend.obtained_head_node, rdf)

class MathOperationsTest(unittest.TestCase):
    """
    Tests to check the working of various math
    operations on Proxy instances.

    """
    def test_add_op(self):
        """
        Test cases to check the working of
        add operation on Proxy instances.

        """
        action_node_1 = Node(None, None)
        action_node_1.value = 10

        action_node_2 = Node(None, None)
        action_node_2.value = 5

        proxy_1 = Proxy(action_node_1)
        proxy_2 = Proxy(action_node_2)

        self.assertEqual(proxy_1 + 1, 11) # Forward addition check
        self.assertEqual(1 + proxy_1, 11) # Reverse addition check

        # Check addition of two different Proxy objects
        self.assertEqual(proxy_1 + proxy_2, 15)

    def test_sub_op(self):
        """
        Test cases to check the working of
        subtract operation on Proxy instances.

        """
        action_node_1 = Node(None, None)
        action_node_1.value = 10

        action_node_2 = Node(None, None)
        action_node_2.value = 5

        proxy_1 = Proxy(action_node_1)
        proxy_2 = Proxy(action_node_2)

        self.assertEqual(proxy_1 - 1, 9) # Forward subtraction check
        self.assertEqual(15 - proxy_1, 5) # Reverse subtraction check

        # Check subtraction of two different Proxy objects
        self.assertEqual(proxy_1 - proxy_2, 5)

    def test_mul_op(self):
        """
        Test cases to check the working of
        product operation ('*') on Proxy instances.

        """
        action_node_1 = Node(None, None)
        action_node_1.value = 10

        action_node_2 = Node(None, None)
        action_node_2.value = 5

        proxy_1 = Proxy(action_node_1)
        proxy_2 = Proxy(action_node_2)

        self.assertEqual(proxy_1 * 2, 20) # Forward multiplication check
        self.assertEqual(2 * proxy_1, 20) # Reverse multiplication check

        # Check product of two different Proxy objects
        self.assertEqual(proxy_1 * proxy_2, 50)

    def test_div_op(self):
        """
        Test cases to check the working of
        division operation on Proxy instances.

        """
        action_node_1 = Node(None, None)
        action_node_1.value = 10

        action_node_2 = Node(None, None)
        action_node_2.value = 5

        proxy_1 = Proxy(action_node_1)
        proxy_2 = Proxy(action_node_2)

        self.assertEqual(int(proxy_1 / 2), 5) # Forward division check
        self.assertEqual(int(15 / proxy_2), 3) # Reverse division check

        # Check division of two different Proxy objects
        self.assertEqual(int(proxy_1 / proxy_2), 2)

    def test_str_op(self):
        """
        Test case to check the working of '__str__'
        implementation in Proxy.

        """
        action_node = Node(None, None)
        action_node.value = 10

        proxy = Proxy(action_node)

        self.assertEqual(str(proxy), '10')

    def test_eq_op(self):
        """
        Test cases to check the working of
        comparison operation on Proxy instances.

        """
        action_node_1 = Node(None, None)
        action_node_1.value = 10

        action_node_2 = Node(None, None)
        action_node_2.value = 10

        proxy_1 = Proxy(action_node_1)
        proxy_2 = Proxy(action_node_2)

        # Comparison with Proxy instance on L.H.S
        self.assertEqual(proxy_1 == 10, True)

        # Comparison with Proxy instance on R.H.S
        self.assertEqual(10 == proxy_1, True)

        # Comparison with Proxy instance on both sides
        self.assertEqual(proxy_1 == proxy_2, True)
