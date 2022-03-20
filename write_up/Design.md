# Design

## High Level System Design

On a high level, the system is decomposed into 5 separate modules, each accounting for a main component of the system. These are `crypto`, `simplify`, `transactions`, `client` and `server`.  Three of these modules,  `crypto`, `simplify`, and `transactions` will all have a folder of unit tests associated with them. 

### Expected File Structure

```
.  
├── README.md  
├── requirements.txt  
├── settle_db.sqlite  
├── setup.py  
├── src  
│   ├── client  
│   │   ├── client.py  
│   │   ├── cli_helpers.py  
│   │   ├── cli.py  
│   │   └── __init__.py  
│   ├── crypto  
│   │   ├── hashes.py  
│   │   ├── __init__.py  
│   │   ├── keys.py  
│   │   ├── rsa.py  
│   │   └── sample_keys  
│   │       ├── d_private-key.pem  
│   │       ├── d_public-key.pe  
│   │       ├── m_private-key.pem  
│   │       ├── m_public-key.pe  
│   │       ├── t_private-key.pem  
│   │       └── t_public-key.pe  
│   ├── __init__.py  
│   ├── server  
│   │   ├── endpoint.py  
│   │   ├── __init__.py  
│   │   ├── models.py  
│   │   ├── processes.py  
│   │   ├── resources.py  
│   │   ├── schemas.py  
│   │   └── setup.py  
│   ├── simplify  
│   │   ├── base_graph.py  
│   │   ├── flow_algorithms.py  
│   │   ├── flow_graph.py  
│   │   ├── graph_objects.py  
│   │   ├── __init__.py  
│   │   ├── path.py  
│   │   └── weighted_digraph.py  
│   └── transactions  
│       ├── __init__.py  
│       ├── ledger.py  
│       └── transaction.py  
├── Test Results - .html  
└── tests  
   ├── graph_renders  
   │   ├── graph0  
   │   ├── graph0.svg  
   │   ├── graph1  
   │   ├── graph1.svg  
   │   ├── graph4  
   │   ├── graph4.svg  
   │   ├── pre_settle0  
   │   ├── pre_settle0.svg  
   │   ├── settled0  
   │   └── settled0.svg  
   ├── test_cli.py  
   ├── test_crypto  
   │   ├── __init__.py  
   │   ├── test_hashes.py  
   │   ├── test_keys.py  
   │   └── test_sign_verify.py  
   ├── test_settling  
   │   ├── __init__.py  
   │   ├── test_flow.py  
   │   ├── test_graph.py  
   │   └── test_Path.py  
   └── test_transactions  
       ├── mock_database.csv  
       ├── graph_renders  
       │   ├── pre_settle0  
       │   ├── pre_settle0.svg  
       │   ├── settled0  
       │   └── settled0.svg  
       ├── __init__.py  
       ├── test_ledger.py  
       └── test_transaction.py
```

### System Module's Interaction
 The best way to show how different parts of the system interact is to consider two operations - `settle sign <transaction>` and `settle simplify <group>`, using a mixture of data flow diagrams and explanation in prose. Between these two commands, every component of my system will be used

#### Sign Flow Diagram 
![[Sign Flow Diagram.png]]

This diagram shows the various processes that should run as a result of the user asking to sign a transaction. 

All client-server communication is done with JavaScript Object Notation (JSON) for this project.

For clarity, the diagram omits an argument to `sign`; `sign` also requires the user's email so that data can be kept in order in the database (more on this when the database design is discussed).

Here, 4 of the 5 modules are used. The `client` and `server` modules are clearly shown. The `transaction` module is used when constructing, signing and verifying transactions.

The `crypto` module is used in the `transaction` object, and provides the methods to be able to sign and verify the `transaction` object. It is also used to load keys on the client side.

#### Simplify Flow Diagram
![[Simplify Flow Diagram.png]]

Everything mentioned in the sign sub-section holds here. However, in the `simplify` command, the `simplify` module is also used. 

The `simplify` module uses elements of the `transaction` module for converting to and from flow graphs and transactions. 

The interactions of different classes are shown diagrammatically below

## Class Diagrams by Module

### Cryptography (`crypto`) Module

![[crypto.jpg]]
Key for this, and all following class diagrams: red m indicates a method, yellow f indicates a field. Method signatures are included, with type hints of parameters where relevant to aid in highlighting relationships. Protected variables are denoted through name - they start with an underscore

Above is a class diagram for the `crypto` module.

The primary objective of this module is to handle all of the security needed by the application. This mainly involves a consistent way to ensure the validity of transactions, as well as their origin. It also will take care of hashing the passwords of users and groups so that they are not stored in plaintext. This is a more minor role, however.

The `RSAPublicKey` and `RSAPrivateKey` objects are lightweight. Their only field is a dictionary, which stores parts of the key, and an identifier. Since an RSA key needs three components to work (when implemented, as it is here, with modular exponentiation encryption/decryption), each component is stored separately in this dictionary. The `__getattr__` method will be overwritten from the `object` parent class so that it is possible to access parts of the key as one would access an attribute (i.e. for the modulus `RSAPublicKey.n`)

#### How RSA Works

RSA is an asymmetric encryption algorithm which works by taking the plaintext (encoded by an integer), raising it to a very large number, and then taking a modulus of a different very large number
$$c = {p^e}\mod{n} ~~~ (1)$$
where $c$ is the ciphertext, $p$ is the plaintext, $e$ is the public exponent, and $n$ is the modulus. How the these numbers are generated is beyond the scope of this project. To decrypt, a similar relationship is used $$p = c^d \mod{n} ~~~ (2)$$
where $d$ represents the private exponent. 

In public key cryptography, everyone has access to the modulus and public exponent in a key, but it is very important that no one except the owner has access to the private exponent. For this reason, I will ensure that the private exponent is never sent across the network. 

To create digital signatures, the process is similar. First, a hash of the message is generated. This is done by the `Hasher` object above. Then, equation $(2)$ is used, with $c$ representing the hash of the message in integer form, as opposed to the ciphertext. Similarly, $p$ now represents the digital signature instead of the plaintext. The signature is then appended to the message. 

To verify the digital signature, equation $(1)$ is used. If the signature is valid, the output of this equation should be the hash of the message. Thus, one hashes the messages and compares it to the outcome of equation $(1)$. If the two match, then the signature is valid. However if they don't match, either the message has been tampered with or the signature has been tampered with.

Thus, it is possible to ensure validity, and verify the origin, of messages.

I will implement this exactly in this way, using the Python builtin `pow()` to carry out the modular exponentiation, and the builtin `hashlib`  library to generate hashes. I will, however, be writing my own interface to `hashlib` to add extra functionality, such as ensuring that all hashes that I generate are padded correctly so that the encryption / decryption works as expected. 

I will also implement the loading of the RSA key in PEM format myself, using regexes to filter out only what I need, and package the resulting numbers into keys accordingly


### Debt Simplification (`simplify`) Module
#### Class Diagram
![[simplify.jpg]]

This is by far the most intricate module, which has complex object-oriented model, complex key data structures, as well as various complex algorithms - both well known and user defined.

The debt simplification module is dedicated to simplifying a graph using the algorithm specified in the analysis section. It does not have any dependencies on any other modules from this project. 

The task of debt simplification is decomposed into four key areas: The flow graph data structure, graph search algorithms, graph flow algorithms, and the assembly of the main simplification interface. 

##### The Flow Graph Data Structure
As I outlined in the project critical path, I wanted to have a basic unweighted digraph data structure, which I could perform breadth first searches (BFS) on before I started to consider flow. To do this, I started with just a `GenericDigraph` class. The graph has only two fields: the `graph`, and the protected field `_backwards_graph`, to aid with the deletion of nodes. 

The graph is effectively represented as an adjacency matrix. I use a dictionary, which maps a node to a list of `edges` ==add edge to class diagram==. `edge` objects contain a `node` field, which represents the destination node, i.e. where the edge is pointing. 

The base graph then has various bookkeeping methods such as checking if nodes are in the graph, checking if a node is associated a list of edges (and vice versa). You can also add and remove nodes and edges.

I also designed a `neighbours` function to return the neighbours of a node, and a `connected()` function, seeing if a node has any connections in the graph.

I mentioned that the `_backwards_graph` was necessary when it comes to deleting nodes. This is because there must be a way of traversing the graph backwards to find which nodes are pointing to the node that you want to delete. If you do not protect against this, then you will end up with edges pointing nowhere. 

The `_backwards_graph` will be managed every time an edge is added / deleted from the graph. When an edge$(u, v)$ is added to the forwards graph, an edge$(v, u)$ is added to the backwards graph. Then, when deleting a node, all that needs to be done is look at the connections of the given node in the backwards graph, and delete the edges from those nodes in the forwards graph. 

This provided everything necessary to implement first search. I opted to do this recursively. The function signature did not fit on the class diagram, so it is included here
```python
def BFS(  
    *,  # star indicates keyword-only args
 graph: graphs.GenericDigraph,  
 queue: BFSQueue,  
 discovered: disc_map,  
 target: src.simplify.graph_objects.Vertex | None,  
 previous: prev_map,  
 neighbours: Callable,  
 do_to_neighbour: Callable = void,  
) -> prev_map:```

Note: `prev_map`  and `disc_map` are not objects but custom type aliases. They are equivalent to

```python
prev_map = dict[src.simplify.graph_objects.Vertex, src.simplify.graph_objects.Vertex | None
]

disc_map = dict[  
    src.simplify.graph_objects.Vertex, src.simplify.graph_objects.Vertex | bool  
]
```

To do the BFS, I first require a queue data structure. I will implement one myself instead of using a builtin. A BFS queue is interesting, as it should not allow for the same element to be enqueued twice. Thus, the data structure I will create will be an ordered set with only two operations: `enqueue()` and `dequeue()`. 

I also need a data structure to keep track of the nodes that had been previously discovered, and where they had been discovered from. This will be important to be able to reconstruct a path through the graph. For this, I will use a dictionary of type `dict[Vertex, Vertex]`, where keys are vertices in the graph and values are where they were discovered from. 

Since the BFS will end up being used in more than one way (searching through the standard graph, or searching for augmenting paths as part of the maxflow algorithm), it is important to describe to it how to look for neighbours. Since functions are first class objects in Python, this is done by passing in the function as and when it is needed.

Similarly with do_to_neighbour, different algorithms that use the BFS will require different things to be done to the neighbours of a node. Hence, this is specified when the function is called, as opposed to when it is defined. 

Here is a python mock-up of how I intend to implement the BFS

```python

@staticmethod  
def BFS(  
     *,  
	 graph: graphs.GenericDigraph,  
	 queue: BFSQueue,  
	 discovered: disc_map,  
	 target: src.simplify.graph_objects.Vertex | None,  
	 previous: prev_map,  
	 neighbours: Callable,  
	 do_to_neighbour: Callable = void,  
	) -> prev_map:  
	  
	 # will only happen if no path to node 
	if queue.is_empty():  
	    return previous  
  
    else:  
        # discover next node in queue  
		current = queue.dequeue()  
        discovered[current] = True  
  
	 # check we haven't been fed a standalone node (i.e. no forward or backwards links)  
		 if not graph.connected(current):  
			if not queue:  
                raise SearchError("Cannot traverse a non connected node", current)  
  
		# if discovered target node return prev  
		 if current == target:  
	            return previous  
  
		else:
            # otherwise, continue on  
			# enqueue neighbours, keep track of whose neighbours they are given not already discovered 
			# do passed in function to neighbouring nodes 
			for neighbour in neighbours(current):  
                if not discovered[neighbour.node]:  
                    previous[neighbour.node] = current  
                    queue.enqueue(neighbour.node)  
  
                do_to_neighbour(current, neighbour.node)  
  
            # recursive call on new state  
			 return Path.BFS(  
			    graph=graph,  
				queue=queue,  
				discovered=discovered,  
				target=target,  
				previous=previous,  
			    neighbours=neighbours,  
				do_to_neighbour=do_to_neighbour,  
			 )
```

After I implement the BFS, I will move onto the max-flow algorithm.

This requires an updating the graph data structure, and the edge data structure. To do this, I will inherit from the `BaseGraph` and `Edge` that I will have already designed. 

The key changes to the edges (in a new class `FlowEdge`) will be:
	 1) Edges will need two new fields: `flow: int` and `capacity: int`, where capacity is a non-negative integer, and flow is an integer
	2) Edges will need a new method: `unused_capacity()`	which will return `capacity` -`flow`
	3) Flow graphs contain a residual edge, as discussed in the Analysis phase. This will be accounted for with a field `residual: bool`. Residual edges will be treated as such.
	4) In order to ease transaction integration later, I will also have edges explicitly track their `src` and their destination (`dest`). This will allow me to build a list of transactions just from a list of edges, but will be discussed further later on.
	5) An `__eq__` function is needed, allowing differentiation between residual edges ^[the `__eq__` function in the base `Edge` class was generated by the `@dataclass` decorater. However, this would fail to differentiate residual edges due to the way that `dataclasses` generates special methods]

The key changes to the graph, in the new class `FlowGraph`, will be:
	1) A backwards graph is no longer needed, instead it will be possible to utilise residual edges to traverse the structure the wrong way when deleting nodes
	2) Adding edges now entails adding a residual edge counterpart, as discussed in the Analysis section. Thus, when edges are removed, their residual edge also needs to be removed. Hence, the `add_edge` and `pop_edge` functions need to be overwritten to work with `FlowEdge` objects.
	3) A `flow_neighbour()` method needs to be introduced, as valid neighbours in the max-flow algorithm are any edges with unused capacity. This is different to a valid neighbour in the BFS, which is any forward-pointing non-residual edge. 
	4) A function is also needed to adjust the edges in the flow graph to become an edge with no flow, and only unused capacity remaining. This is added under the identifier `adjust_edges()`

In the analysis section, I detailed how the Edmonds-Karp max-flow algorithm works. I will implement it exactly as described in the analysis section. All of the methods which are involved in finding the max-flow through a flow graph will be contained in the `flow_algorithms.MaxFlow` object. I will decompose the task of finding the max_flow into 5 functions. Their signatures are listed below

```python
class MaxFlow:  
    
    @staticmethod  
	def edmonds_karp(graph: FlowGraph, src: Vertex, sink: Vertex) -> int:  ...
    
    @staticmethod  
	def augmenting_path(graph: FlowGraph, src: Vertex, sink: Vertex) -> list[Vertex]:  ...
	
    @staticmethod  
	def bottleneck(graph: FlowGraph, node_path: list[Vertex]) -> int: ...  
  
    @staticmethod  
	def augment_flow(graph: FlowGraph, node_path: list[Vertex], flow: int) -> None: ...  
	 
	@staticmethod
	def nodes_to_path(graph: FlowGraph, nodes: list[Vertex]) -> list[FlowEdge]:  ...

```

`augmenting_path` makes use of the recursive breadth first search that will have been implemented to find the shortest path through the graph from the source node to the sink node. `nodes_to_path` will be used to convert the list of nodes returned by the BFS function to a path. `bottleneck` will return the bottleneck of a path through the graph, and `augment_flow` will augment the flow of a path, changing the `flow` field in each `FlowEdge`. These are all combined in the  `edmonds_karp` function to return an integer - the maximum flow from the given source node to the given sink node. 

A python mock up of the implementation of the `edmonds_karp` function is given here

```python
def edmonds_karp(graph: FlowGraph, src: Vertex, sink: Vertex) -> int:  
  
    max_flow = 0  
  
	while aug_path := MaxFlow.augmenting_path(graph, src, sink):  
	    bottleneck = MaxFlow.bottleneck(graph, aug_path)  
        max_flow += bottleneck  
  
        MaxFlow.augment_flow(graph, aug_path, bottleneck)  
        # graph.to_dot()  
  
	return max_flow
```


With all of the components having been designed, it is possible to integrate the process entirely. The `Simplify` class has one method: `simplify_debt(graph: FlowGraph)`. This combines all of what is above into my user-defined algorithm to simplify the graph as a whole. Again, this algorithm works exactly as laid out in the analysis section. 

For every edge in the graph, a max-flow is run between the nodes at either end of the edge. This changes the state of the graph, as augmenting the flow through the graph has the possibility of changing the flow on each edge / residual edge. 

After the max-flow is run, an edge is added to the clean graph with a weight of the max-flow, and the `adjust_edges()` method is run on the 'initial' graph (initial in inverted commas because, of course, its state will have been changed by the algorithm. Calling it 'initial' just differentiates it from the clean graph that I building along the way).  

This process should continue until there are no more edges in the 'initial' graph. 

In pseudocode
```python
for edge(u, v) in graph:  
	if new := maxflow(u, v): 
		clean.add_edge(u, (v, new))
		messy.adjust_edges()
```


### Transaction integration (`transactions`) module


