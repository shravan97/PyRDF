# PyRDF - A Python library for Dataframe computation using ROOT

### Table of Contents

[Module-wise documentation](#module-wise-documentation)
- [CallableGenerator.py](#callablegeneratorpy)  
	- [Class : CallableGenerator](#class--callablegenerator)
- [Node.py](#nodepy)
	- [Class : Node](#class--node)
- [Operation.py](#operationpy)
	- [Class : Operation](#class--operation)
- [Proxy.py](#proxypy)
	- [Class : Proxy](#class--proxy)
- [RDataFrame.py](#rdataframepy)
	- [Class : RDataFrame](#class--rdataframe)
	- [Class : RDataFrameException](#class--rdataframeexception)
- [` __init__.py `](#__init__py)
	- [Module : ` __init__.py `](#module--__init__py)
- [backend/Backend.py](#backendbackendpy)
	- [Class : Backend](#class--backend)
- [backend/Local.py](#backendlocalpy)
	- [Class : Local](#class--local)
- [backend/Dist.py](#backenddistpy)
	- [Class : Dist](#class--dist)
- [backend/Spark.py](#backendsparkpy)
	- [Class : Spark](#class--spark)
- [backend/Utils.py](#backendutilspy)
	- [Class : Utils](#class--utils)


### Module-wise documentation
#### CallableGenerator.py
- #### Class : CallableGenerator
    Description : *Utility class to generate a callable to traverse the PyRDF graph*

	- **Constructor** : `__init__`
		- This takes in the root or head node of the required PyRDF graph and sets it to an instance member `head_node` .
	- **Instance data members**
		- `head_node` 
			- This represents the root node of the current PyRDF graph that we’re dealing with. This is taken in as an argument to the constructor of `CallableGenerator`.
	- **Methods**
		- `get_callable` 
			- This method returns a function (called `mapper`) that takes in a [PyROOT](https://root.cern.ch/pyroot) RDataFrame object as input.
			- Logic used in the mapper : 
				- The mapper recursively traverses through the PyRDF operations graph starting from the `head_node` instance member and recursively executes those operations on the input PyROOT RDataFrame object.
				- While recursing, it collects the computed values of all action nodes (like `Count`, `Histo1D`, `Histo2D`, ...etc.) and finally returns the entire list (of computed values of action nodes) from the first recursive state.
				- Take a look at the below picture for some clarity :


		- `get_action_nodes` 
			- This does almost the exact same thing as the mapper function, except that, this doesn’t execute the operations and this returns all nodes as they are (as Node objects). The list of nodes returned from this method correspond to the list of values returned from the mapper. Hence, this can be used when you need to set the values of action nodes onto the value data members of the node objects.

#### Node.py
- #### Class : Node
	Description : *Represents a node in the computational graph of operations*

	- **Constructor** : `__init__` 
		- Logic used : 
			- If `get_head` is None , it is assumed that the current node is the head node. Hence, if `get_head` is `None`, `get_head` is lambda function that returns itself. Otherwise, it simply returns the head node.
			- `get_head` points to a function that returns the head node instead of pointing to the head node itself. This is because, by using a function, the object gets garbage collected after the user stops referencing it. Whereas, if `get_head` points to the head node itself directly, then it will not be garbage collected by Python when the user stops referencing it. This logic plays an important role in pruning the graph before execution.
			- `children` is set to an empty list and value is set to None initially.

	- **Instance data members**
		- `operation` 
			- The operation that has to be executed on the current node in the computational graph.
		- `children` 
			- The list of children nodes to the current nodes in the computational graph.
		- `value` 
			- The value of the current node after execution. This is applicable only to action nodes.
		- `get_head` 
			- A lambda function that returns the head node of the current computational graph.
	- **Methods**
 		- `__getstate__` 
			- This method is used to make `Node` objects serializable (pickle-able). This collects children and operation attributes as a Python dictionary (with string keys) and returns the dictionary to the callee. The attribute `get_head` isn’t stored here because it is not required for any computation in the clusters.
		- `__setstate__` 
			- This method enables un-pickling of the pickled representation of `Node` objects. This method simply sets the attributes from the pickled state dictionary ( that `__getstate__` would’ve returned).
		- `__getattr__` 
			- This method intercepts all attribute calls (except dunder method calls) and sets the method name onto an instance variable `_cur_attr` (temporary). This returns the `_call_handler` method, to which arguments could be passed.
		- `_call_handler` 
			- Logic used : 
				- Check if the new operation call on the current node is supported by the current backend first. If it’s supported, create a new operation based on the call (else, `Backend`'s `check_supported` function itself raises an error). 
				- Create a new node and encapsulate the new operation. 
				- Append this new node to the `children` instance member.
				- If the new node is an action node, return a `Proxy` object to the new node. Else, return the new node itself.
		- `graph_prune` 
			- This method recursively prunes all children nodes based on user references and returns `True` if the current node itself has to be pruned. Otherwise, returns `False`.
			- Logic used : 
				- Iterate through children and make a call to the `graph_prune` method of each child.
				- Create a new children list for the current node and only append the `graph_prune` calls that returned `False`.
				- Finally determine if the current node has to be pruned with the help of the user references to the current node. Here, the `gc` module is used to get the referrers to a given node. 
				- If the current node is a leaf node (`no. of children = 0`) and if the number of user references to the current node is less than or equal to 3, then simply prune this. The references that should exist for a node to not be pruned are : 
					- User reference (usually through a variable)
					- Parent node’s reference
					- Reference to the `graph_prune` function (because we’re inside it while checking for references)
					- An internal reference (which every Python object has)
				- Hence, any leaf node with less than 4 references will return `False` .
#### Operation.py
- #### Class : Operation
	Description : *Represents a valid ROOT operation*

	- **Constructor** : `__init__` 
		- This takes in the operation’s name (string), operation’s arguments and operation’s named arguments as parameters and sets them to their respective instance variables. The instance data member `op_type` is also being set here, by a call to the private function `_classify_operation` .
	- **Static data members**
		- `Types` 
			- This is an `Enum` object that takes 2 possible values, `ACTION` or `TRANSFORMATION` . This is used to represent the operation type everywhere in this package
	- **Instance data members**
		- `name` 
			- This represents the name of the current operation.
		- `args` 
			- This represents the arguments that are to be passed onto the current ROOT operation call.
		- `kwargs` 
			- This represents the named arguments that are to be passed onto the current ROOT operation call.
		- `op_type` 
			- This is an Enum object that represents the type of current operation.
	- **Methods**
		- `_classify_operation` 
			- This method classifies the current operation and returns an `Enum` type.
			- Logic used for classification : 
				- Look up the current operation by name in the dictionary of operations (`operations_dict`) defined inside `_classify_operation` .
				- If the current operation exists in `operations_dict` , then return the type directly.
				- Else, raise an exception that the current operation is invalid.
		- `is_action` 
			- A helper method to check if the current operation is an action.
		- `is_transformation` 
			- A helper method to check if the current operation is a transformation.

#### Proxy.py
- #### Class : Proxy
	Description : *Represents a proxy to the value of an action node*

	- **Constructor** : `__init__` 
		- This takes in an `action_node` (A node object that encapsulates an `ACTION` operation) as a parameter and sets it to the instance member of the same name.
	- **Instance data members**
		- `action_node` 
			- This represents the action node, whose value the current instantiation is a proxy to.
	- **Methods**
		- `__getattr__` 
			- This method intercepts all non-dunder attribute calls to the current Proxy object. It sets a temporary instance variable `_cur_attr` and returns the function `_call_handler`, to which the user can pass in arguments.
		- `GetValue` 
			- This method checks if the current node's value was computed before. If the value doesn't exist, the execution is triggered by calling the `execute` method on the `current_backend`.
		- `_call_handler` 
			- This method takes in arguments (named as well as unnamed) and performs a function call (that was requested by the user) to the current action node’s value if it exists. Otherwise, it triggers the event-loop using backend’s `execute` function. 
			- The function call is performed using the built-in `getattr` method. The output of this call is returned.

#### RDataFrame.py
- #### Class : RDataFrame
	Description : *Equivalent to ROOT Python’s RDataFrame*

	- **Constructor** : `__init__` 
		- Takes in required arguments, processes them and sets them as a list to the instance variable args .
		- Logic used : 
			- Convert the `args` tuple to a list inorder to make it mutable.
			- Convert all Python lists in the arguments to ROOT C++ vectors with the help of the private method `_get_vector_from_list` .
			- Pass these arguments as it is to PyROOT’s RDataFrame constructor.
			- If a TypeError occurs, raise a `RDataFrameException` .
			- Else, store the args as they are.
	- **Instance data members**
		- `args` 
			- This represents the arguments to `RDataFrame` constructor contained in a Python list.
	- **Methods**
 		- `_get_vector_from_list` 
			- This method converts the input list to a ROOT C++ vector with the help of PyROOT’s `ROOT.std.vector`.
		- `get_num_entries` 
			- This method computes the total number of entries in the input dataset based on the input arguments.
			- Logic used :
				- If the arguments list consists of only one integer, then simply return that integer.
				- Otherwise, if the arguments list consists of only one element of the type `ROOT.TTree` , then compute and return the number of entries by calling the `GetEntries` method on that argument.
				- Else, create a `ROOT.TChain` using the arguments and call the `GetEntries` method on the `ROOT.TChain` object to compute and return the number of entries.

- #### Class : RDataFrameException
	Description : *A separate type of Exception to handle incorrect arguments to RDataFrame constructor*

	- #### Constructor : `__init__` 
		- This takes in an exception and a string message as input and simply calls the super class `Exception` passing the input exception to it and additionally printing the string message that was given in as an argument.


#### `__init__.py`
- #### Module : `__init__`
	Description : *Initializes PyRDF package*

	- **Global variables**
		- `current_backend` 
			- This refers to an instance of the chosen backend by the user. This is set using `PyRDF.use` method.
		- `includes` 
			- This represents the list of paths to header files that need to be declared before execution of computational graph. This list is extended using `PyRDF.include` method.
	- **Methods**
		- `use` 
			- This method takes in an optional string and an optional dictionary as arguments. The string represents user’s backend choice, which could be either “local” or “spark”. The dictionary represents the configuration parameters for the chosen backend.
			- **NOTE** :- If `use` method was never invoked to set a backend choice, then “local” would be the default backend.
		- `include` 
			- This method takes in a list of strings which represent the path to C++ header files. All the elements of this list are simply appended to the global variable `includes` . This method also accepts a string, which is internally converted to a single-element list.

#### backend/Backend.py
- #### Class : Backend
	Description : *Base class for all backend implementations*

	- **Constructor** : `__init__` 
		- This takes in a parameter named `config` and assigns it to the `config` instance member. This should be a Python dictionary with all necessary configuration parameters required for the chosen backend.
	- **Instance data members**
		- `config` 
			- This is a Python dictionary that represents the configuration parameters required for the chosen backend enviroment. For example, Spark’s `config` member would have it’s configuration parameters like `spark.master` , `spark.executor.instances`, `spark.app.name` ... etc.
			- This member is taken in set by the constructor of this class.
		- `supported_operations` 
			- This is a list of operations that are supported by the current backend. This is declared as a static member in `Backend` class. 
			- But, If you want to create your own backend implementation and change this list, you should change it as an instance member. This is because, the instance member `supported_operations` is what will be used in `check_supported` instance method to check if an operation is supported or not.
	- **Methods**
		- `check_supported` 
			- This method takes in an operation name (string) as a parameter and checks the `supported_operations` instance member for the operation. If it doesn’t exist, it raises an exception that the requested operation isn’t supported in the current backend. Otherwise, it returns `None`.
		- `execute` (*abstract method*)
			- This is an abstract method that needs to be implemented by a child Backend. This takes in an instance of `CallableGenerator` as a parameter. 
			- This method should trigger the event-loop and set the values to their corresponding nodes.
			- Refer to the `Local` implementation for a better picture.

#### backend/Local.py
- #### Class : Local
	Description : *Implementation of Local backend*

	- **Parent class** : `Backend` 
	- **Constructor** : `__init__` 
		- This calls the constructor of the super class (`Backend`) passing in the `config` parameter.
		- Then it constructs the `supported_operations` instance variable by excluding the operations that aren’t supported in `Local` implementation.
		- Before constructing the `supported_operations` list, there’s a check for Multi-threading using `ROOT.ROOT.IsImplicitMTEnabled()`. If Multi-threading is enabled, “Range” operation would not be supported and would not be added to the `supported_operations` list. Otherwise, it would be added.
	- **Methods**
		- `execute` 
			- This is the implementation of abstract execute method from `Backend` class. This takes in an instance of `CallableGenerator` as a parameter and uses it to get the callable function.
			- The required header files are then declared using `declare_headers` method from `Utils` class.
			- Then, a PyROOT RDataFrame object is passed to the callable function and it executes all the operations recursively on the RDataFrame object. The event-loop triggered by calling `GetValue()` on the first of the obtained values.
			- The obtained values and result proxies are then stored in the corresponding node objects.
			- Notice that all execution here happens in your local system as opposed to distributed backends.

#### backend/Dist.py
- #### Class : Dist
	Description : *Implementation of Dist backend and the base class for all distributed backends*

	- **Parent class** : `Backend` 
	- **Constructor** : `__init__` 
		- This calls the constructor of the super class (`Backend`) passing in the `config` parameter.
		- Then, the operations that aren’t supported are removed from `supported_operations` list.

	- **Instance members**
		- `supported_operations` and `config` 
			- Same as in `Backend.py` 

	- **Methods**
		- `BuildRanges` 
			- This method takes in the number of partitions to divide the dataset into (`npartitions`) and the total number of entries in the dataset (`nentries`). It then creates range pairs (a Python list with range tuples, for example., `[(1, 2), (2, 3)]` ) with the following algorithm : 
				- Initialize ranges variable with an empty Python list.
				- Calculate nentries % npartitions and assign it to a variable. Let’s call this variable remainder .
				- Start a while loop with the iterator ( i ) initially at 0.
				- Assign the start of the current range as the current value of the iterator i . 
				- If the current value of remainder is non-zero, then add a ‘1’ to the end value of the current range and the current value of the iterator.
				- Then, simply create a tuple with the start and end values as the only two elements and append it to the end of the ranges list.
		- `execute` 
			- Define the mapper and reducer functions : 
				- `mapper`  
					- This takes in a range pair (a Python tuple with start and end values of the range) and runs all requested operations on the elements in the dataset that lie within the given range.
					- The headers files included as a part of `PyRDF.include` are declared using the `declare_headers` method in `Utils` module.
					- Then, a PyROOT RDataFrame object is created using the arguments given to PyRDF’s RDataFrame object initially.
					- This RDataFrame object is then passed onto the callable that gets generated using the `CallableGenerator` instance that was given in to the `execute` method.
					- The output of the callable is a list of `RResultPtr`s.
					- Since these RResultPtrs are not serializable, the values are copy constructed and they replace their respective RResultPtrs in the list.
				- `reducer` 
					- This method takes in two PyRDF value lists (each of them is produced by the `mapper`).
					- It merges the two lists based on the type of each element in the lists.
					- It is safe to assume here that the corresponding values in the two lists will be of the same type (because they ran through the same computational graphs)
					- Merging of objects of type `ROOT.TH1` or `ROOT.TH2` is done using the `Add` method in such objects. Those objects in the second values list are added onto the correspoding objects in the first values list and subsequently the first list is returned.
					- Merging objects of type `ROOT.TGraph` is done with the help of the `Merge` method in such objects. But, the `Merge` method only accepts objects of type `ROOT.TCollection`. Hence, we create a temporary `ROOT.TList` (which is child type of `ROOT.TCollection`) to put in our second `ROOT.TGraph` object and this is passed onto the `Merge` call on the first `ROOT.TGraph` object.
					- If we encounter any other type of object while merging, simply raise a `NotImplementedError`.

				- After the declaration of the `mapper` and `reducer` functions, we get the value of the number of entries (`nentries`) for the input dataset. This is done using `get_num_entries` instance method of `RDataFrame` class.
				- If this `nentries` is `0`, we fall back to local execution.
				- We then call the `ProcessAndMerge` method that invokes the `mapper` and `reducer` functions. The output of this call is the final list of values after computational graph execution.
				- We also get all the action node objects in the same order as their values (returned by `ProcessAndMerge`) using` CallableGenerator`‘s `get_action_nodes` .
				- We then assign the respective values to the value attribute of node object.

#### backend/Spark.py
- #### Class : Spark
	Description : *Implementation of Spark distributed backend*

	- **Parent class** : `Dist` 
	- **Constructor** : `__init__` 
		- This calls the constructor of the super class (`Dist`) passing in the `config` parameter.
		- Then, the `npartitions` parameter is removed (popped) from the `config`  dictionary to assign it to a separate instance variable named `npartitions`.
		- The rest of the key-value pairs are passed onto the `SparkConf` constructor to create a new `SparkConf` instance. This `Sparkconf` instance is then passed onto the `getOrCreate` method of `SparkContext` class to create a new `SparkContext` instance.
	- **Instance members**
		- `npartitions` 
			- This represents the number of parts that the input dataset should be divided into before processing each part. If this value is not specified by the user, it takes the value of `spark.executor.instances` from the `config` dictionary. If `spark.executor.instances` is also not specified by the user, `npartitions` is assigned the value 2.
		- `sparkContext` 
			- This uses the `config` dictionary after excluding `npartitions` parameter to first create a `SparkConf` instance and then a `SparkContext` instance using that. The `SparkConf` instance is passed onto the `getOrCreate` method in `SparkContext` class.
	- **Methods**
		- `ProcessAndMerge` 
			- This method takes in a `mapper` function and a `reducer` function and then performs Map-Reduce using Spark.
			- First, we obtain the range pairs using `BuildRanges` method from the parent class (`Dist`).
			- Then, we create a parallel collection using the `parallelize` instance method in `Sparkcontext`.
			- Map-Reduce is performed using `sparkContext.map(mapper).treeReduce(reducer)` , the output of which is simply returned.

#### backend/Utils.py
- #### Class : Utils
	Description : *A Class that houses utility functions*

	- **Class methods**
		- `declare_headers` 
			- This takes in a list of strings that represents paths to required C++ header files.
			- Each of these header files are declared using `ROOT.gInterpreter.Declare` call.
			- If `ROOT.gInterpreter.Declare` call returns `-1`, then we raise an exception as ROOT would’ve encountered an error while declaring the header file.
