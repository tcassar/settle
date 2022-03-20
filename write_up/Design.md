# Design

QUESTIONS
1) Ask about need to add data integrity (i have and its all sorted, does it need to go in here?)
2) Enough on HCI?
3) Enough on client side?


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

The interactions of different classes are shown diagrammatically below

## Class Diagrams by Module
### Cryptography (`crypto`) Module

![[crypto.jpg]]
Key for this, and all following class diagrams: red m indicates a method, yellow f indicates a field. Method signatures are included, with type hints of parameters where relevant to aid in highlighting relationships. Protected variables are denoted through name - they start with an underscore

Above is a class diagram for the `crypto` module.

The primary objective of this module is to handle all the security needed by the application. This mainly involves a consistent way to ensure the validity of transactions, as well as their origin. It also will take care of hashing the passwords of users and groups so that they are not stored in plaintext. This is a more minor role, however.

The `RSAPublicKey` and `RSAPrivateKey` objects are lightweight. Their only field is a dictionary, which stores parts of the key, and an identifier. Since an RSA key needs three components to work (when implemented, as it is here, with modular exponentiation encryption/decryption), each component is stored separately in this dictionary. The `__getattr__` method will be overwritten from the `object` parent class so that it is possible to access parts of the key as one would access an attribute (i.e. for the modulus `RSAPublicKey.n`)

#### How RSA Works

RSA is an asymmetric encryption algorithm which works by taking the plaintext (encoded by an integer), raising it to a very large number, and then taking a modulus of a different very large number
$$c = {p^e}\mod{n} ~~~ (1)$$
where $c$ is the ciphertext, $p$ is the plaintext, $e$ is the public exponent, and $n$ is the modulus. How the these numbers are generated is beyond the scope of this project. To decrypt, a similar relationship is used $$p = c^d \mod{n} ~~~ (2)$$
where $d$ represents the private exponent. 

In public key cryptography, everyone has access to the modulus and public exponent in a key, but it is very important that no one except the owner has access to the private exponent. For this reason, I will ensure that the private exponent is never sent across the network. 

To create digital signatures, the process is similar. First, a hash of the message is generated. This is done by the `Hasher` object above. Then, equation $(2)$ is used, with $c$ representing the hash of the message in integer form, as opposed to the ciphertext. Similarly, $p$ now represents the digital signature instead of the plaintext. The signature is then appended to the message. 

To verify the digital signature, equation $(1)$ is used. If the signature is valid, the output of this equation should be the hash of the message. Thus, one hashes the messages and compares it to the outcome of equation $(1)$. If the two match, then the signature is valid. However, if they don't match, either the message has been tampered with or the signature has been tampered with.

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

The graph is effectively represented as an adjacency matrix. I use a dictionary, which maps a node to a list of `edges` ==TODO: add edge to class diagram==. `edge` objects contain a `node` field, which represents the destination node, i.e. where the edge is pointing. 

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

Similarly, with do_to_neighbour, different algorithms that use the BFS will require different things to be done to the neighbours of a node. Hence, this is specified when the function is called, as opposed to when it is defined. 

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
	5) An `__eq__` function is needed, allowing differentiation between residual edges ^[the `__eq__` function in the base `Edge` class was generated by the `@dataclass` decorator. However, this would fail to differentiate residual edges due to the way that `dataclasses` generates special methods]


The key changes to the graph, in the new class `FlowGraph`, will be:
	1) A backwards graph is no longer needed, instead it will be possible to utilise residual edges to traverse the structure the wrong way when deleting nodes
	2) Adding edges now entails adding a residual edge counterpart, as discussed in the Analysis section. Thus, when edges are removed, their residual edge also needs to be removed. Hence, the `add_edge` and `pop_edge` functions need to be overwritten to work with `FlowEdge` objects.
	3) A `flow_neighbour()` method needs to be introduced, as valid neighbours in the max-flow algorithm are any edges with unused capacity. This is different to a valid neighbour in the BFS, which is any forward-pointing non-residual edge. 
	4) A function is also needed to adjust the edges in the flow graph to become an edge with no flow, and only unused capacity remaining. This is added under the identifier `adjust_edges()`
	5) A way of verifying that the settling has resulted in a fair graph, where people owe and are owed the same (net) amount of money as they originally were. This is done with the `net_debt` field, which is a `dict[Vertex, int]`

In the analysis section, I detailed how the Edmonds-Karp max-flow algorithm works. I will implement it exactly as described in the analysis section. All the methods which are involved in finding the max-flow through a flow graph will be contained in the `flow_algorithms.MaxFlow` object. I will decompose the task of finding the max_flow into 5 functions. Their signatures are listed below

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


With all the components having been designed, it is possible to integrate the process entirely. The `Simplify` class has one method: `simplify_debt(graph: FlowGraph)`. This combines all of what is above into my user-defined algorithm to simplify the graph as a whole. Again, this algorithm works exactly as laid out in the analysis section. 

For every edge in the graph, a max-flow is run between the nodes at either end of the edge. This changes the state of the graph, as augmenting the flow through the graph has the possibility of changing the flow on each edge / residual edge. 

After the max-flow is run, an edge is added to the clean graph with a weight of the max-flow, and the `adjust_edges()` method is run on the 'initial' graph (initial in inverted commas because, of course, its state will have been changed by the algorithm. Calling it 'initial' just differentiates it from the clean graph that I'm building along the way).  

This process should continue until there are no more edges in the 'initial' graph. 

In pseudocode
```python
for edge(u, v) in graph:  
	if new := maxflow(u, v): 
		clean.add_edge(u, (v, new))
		messy.adjust_edges()
```

Once the simplification has concluded, the net debts of the new graph should be compared with the (cached) net debts of how the graph was initially. These should always be identical, and the simplification process will raise an error if this is not the case, indicating that simplification should be aborted and retried.

### Transaction integration (`transactions`) module

![[Transaction class diagram.jpg]]

==TODO: add flow graph composition to ledger.Ledger==

The purpose of the `transactions` module is to combine the `crypto`  and `simplify` module,  to allow transactions between people to be created, signed and verified. A `Ledger` object will also be introduced to represent a group of transactions, and with the ability to simplify them, ensuring that they are all verified before doing so. 

Since this module is effectively the assembly through aggregation and composition of the `crypto` and `simplify` modules, it does not have much in the way of complex data structures or algorithms. 

Signatures are stored as bytes inside the transaction object. Time is stored as a `datetime.datetime` object, and keys are stores as `crypto.keys.RSAPublicKey` objects (as per class diagram). 

Ledger's `ledger` field is a list of `transaction` objects. Its `nodes` field is a list of all the people in the ledger, used to generate the flow graph that it creates to simplify transactions. `key_map` keeps track of which key belongs to which user ID. 

The `Transaction` class inherits from the `Signable` class. This happens due to the order in which I intend to implement the project. The `crypto` module comes first, and I need to be able to test signing objects before I have transactions in place. This is also advantageous to me in case I decide to continue this project in the future and want to differentiate between different things that each need signing. 

### Server-side (`server`) module
![[server high level.jpg|400]]
![[server schemas and models with fields and methods.png]]

#### API Endpoints and Resources 

A lot of the work of the server is in serialising and deserialising objects / JSON. I will do this using the `marshmallow` library for Python. This requires that schema objects are set up with the same fields as the objects you want to serialise from / deserialise to.

This means that a lot of boilerplate code is needed, so I will not talk to much about that here as it is not particularly interesting, and does not prevent me from having a fully considered design of my problem.

I thought it more important to discuss the resources and endpoints that I would need to serve over my API. My resources are listed in the class diagrams above, and all serve an important purpose.

```python
Group, "/group/<int:id>", "/group"
PrettyTransaction, "/transaction", "/transaction/<string:email>"
User, "/user/<string:email>", "/user"
UserGroupBridge, "/group/<int:id>/<string:email>", "/group/<string:email>"
TransactionSigVerif, "/transaction/auth/<int:id>"
Simplifier, "/simplify/<int:gid>"
Debt, "/user/debt/<string:email>"
GroupDebt, "/user/debt/<string:email>/<int:id>"
```

This shows the `Resource` child classes as shown in the class diagram above with their endpoints. 

A lot of the above resources implement GET and POST, which are self-explanatory by design in most cases (i.e. GET "user/<string:email> will return user data for a given email"). I will discuss certain less obvious resources and enpoints.

`PrettyTransaction` is a transaction object that is intended for being viewed on the front end by a user. It has people saved as emails as opposed to IDs, an association with a group, no keys involved, the time of creation, reference, and verification status. It also has the transaction ID. The POST method of pretty transaction is used to post new transactions to the database. This is because the details entered by the user about new transactions line up exactly with the pretty transaction schema. All processing such as adding public keys and user IDs is done by the server. 

`UserGroupBridge` also warrants discussion. The resource implements POST and GET. POST will add a user to a group, and GET will get all groups associated with a given user. 

`TransactionSigVerif` implements GET and PATCH. GET will verify a transaction, returning copy of verified transaction. PATCH will, upon receiving a signature, check that the signature is valid with data from the database (public key data, etc), and if the signature is valid, the signature will be inserted into the database on the given transaction ID. 


I intend to run the API using `flask` and `flask_restful`; two commonly used Python libraries for such purpose. During testing, I will run the server on a Raspberry Pi 


---
#### Database Access

The server module will handle all interactions with the sqlite3 database (entity relationship diagram below)

![[ER Diagram.png]]

Here is the same database's DDL

```sqlite
create table groups
(
    id       INTEGER
        primary key autoincrement,
    name     TEXT not null,
    password TEXT not null
);

create unique index groups_group_id_uindex
    on groups (id);

create table keys
(
    id INTEGER
        primary key autoincrement,
    n  TEXT,
    e  TEXT
);

create table sqlite_master
(
    type     text,
    name     text,
    tbl_name text,
    rootpage int,
    sql      text
);

create table sqlite_sequence
(
    name,
    seq
);

create table users
(
    id       INTEGER
        primary key autoincrement,
    name     TEXT,
    email    TEXT,
    password TEXT,
    key_id   INTEGER
        references keys (key_id)
);

create table group_link
(
    id       INTEGER
        primary key autoincrement,
    group_id INTEGER
        references groups (group_id),
    usr_id   INTEGER
        references users (usr_id)
);

create table pairs
(
    id      INTEGER
        primary key autoincrement,
    src_id  INTEGER
        references users (usr_id),
    dest_id INTEGER
        references users (usr_id)
);

create unique index uniq_pair
    on pairs (src_id, dest_id);

create table transactions
(
    id               INTEGER
        primary key autoincrement,
    pair_id          INTEGER not null
        references pairs,
    group_id         INTEGER not null
        references groups,
    amount           INTEGER,
    src_key          INTEGER not null
        references keys,
    dest_key         INTEGER not null
        references keys,
    reference        TEXT,
    time_of_creation TEXT,
    src_sig          TEXT    default '',
    dest_sig         TEXT    default '',
    settled          INTEGER default 0 not null,
    verified         integer default 0 not null
);
```


Since this is a fairly complex relational database system, I put some thought into the queries that I would use to select data. Below is an example of such a query.

```sqlite

SELECT transactions.id, group_id, amount, reference, time_of_creation, u2.email, verified 
FROM transactions  
INNER JOIN pairs p on p.id = transactions.pair_id 
INNER JOIN users u on u.id = p.src_id 
INNER JOIN users u2 on u2.id = p.dest_id 
WHERE transactions.settled = 0 AND u.email = ?;
   
SELECT transactions.id, group_id, amount, reference, time_of_creation, u2.email, verified 
FROM transactions  
INNER JOIN pairs p on p.id = transactions.pair_id 
INNER JOIN users u on u.id = p.dest_id 
INNER JOIN users u2 on u2.id = p.src_id 
WHERE transactions.settled = 0 AND u.email = ?;

```

These are two separate queries intended to retrieve two separate things from the database - they are to return rows of data that can be used to build a `models.PrettyTransaction` object. In the first case, data is fetched where the user's email provided is the source of the transaction - i.e. it will retrieve a user's outgoing transactions. The second query returns the transactions in which the user is owed money. 

These statements are not group specific, but will return all transactions that have not been settled. 

#### Server Logic
The server is, of course, more than just an API and database access - it will carry out the vast majority of the data processing. In that sense, my client server models is effectively thick server, thin client.

As with the endpoints, a lot of the logic is minimal and self explanatory by design. Thus, here I will discuss two of the more intensive processes that the server can be asked to do. 

##### Signing a transaction
Below is a swim lane diagram to aid my explanation of how a transaction is signed

![[Sign Flow Diagram.png]]

This diagram shows the various processes that should run as a result of the user asking to sign a transaction. 

All client-server communication is done with JavaScript Object Notation (JSON) for this project.

For clarity, the diagram omits an argument to `sign`; `sign` also requires the user's email so that data can be kept in order in the database (more on this when the database design is discussed).

Here, 4 of the 5 modules are used. The `client` and `server` modules are clearly shown. The `transaction` module is used when constructing, signing and verifying transactions.

The `crypto` module is used in the `transaction` object, and provides the methods to be able to sign and verify the `transaction` object. It is also used to load keys on the client side.

##### Simplifying a group of transactions

![[Simplify Flow Diagram.png]]

This is in many ways the most important process in the project. Upon being asked to settle a group, every part of the project will be used. 

In the implementation, all I will need to do is query the database with a query such as 
```sqlite
SELECT transactions.id, src_id, dest_id, src_sig, dest_sig,  
 amount, reference, time_of_creation, group_id, k.e, k.n,  
 k2.e, k2.n  
FROM transactions  
JOIN keys k on k.id = transactions.src_key  
JOIN keys k2 on k2.id = transactions.dest_key  
JOIN pairs p on p.id = transactions.pair_id  
WHERE transactions.group_id = ?;
```

to get all of the data needed to build a `transaction.ledger.Ledger` of `transaction.transaction.Transaction` objects. Once those objects are build, all that needs to happen is I write `ledger.simplify_ledger()`. This will then invoke all of the logic discussed in the `simplify` module section, as well as handle the verification of signatures, as discussed in the `crypto` module section.  This will be wrapped in a `try: ... except: ...` clause, and any errors will be returned with a 40X error code and reason for failure.

### Client-side (`client`) module
As aforementioned,  the client is a thin client, meaning it does not have many responsibilities in the overarching structure of the program. Thus, this section will mainly be examples and mock ups of the elements of Human-Computer Interaction.

To show this, I will provide screenshots of an output to STDOUT of how I would like certain outputs to look. Here I will provide mainly ancillary outputs. and how I would like certain prompts to appear upon a command being run

* Upon a user registering a new account
![[Pasted image 20220320220345.png]]

The program should prompt the user with the details that they need to enter to create their account. Password entering should be hidden, as it is commonly in CLIs.
Passwords should be confirmed through asking for confirmation, as above. If the passwords entered do not match, the program should ask to user re enter thir password. The program should report a failure if an invalid path to a key is given, as here

* Upon creating & joining a group
![[Pasted image 20220320221811.png]]

* An example of how a failed attempt at an action should look is
![[Pasted image 20220320222431.png]]

+ Finally, viewing existing transactions should look like this

![[Pasted image 20220320223545.png]]

This is not an exhaustive list, but is the general blueprint of how interaction should look. Every possible actions will end up looking like one of these above templates, be it something like simplifying or signing a transaction, which will just result in a confirmation, or seeing all of the open transactions in the group, which will look the same as seeing all of your open transactions. 

The full list of commands that I would like the user to be able to enter is below

```
Usage: settle register [OPTIONS]  

	Registers a new user

Options:  
 --name TEXT  
 --email TEXT  
 --password TEXT  
 --pub_key PATH  
 --help           Show this message and exit.
```

```
Usage: settle whois [OPTIONS] EMAIL  

	Returns a user's public key info given their email

Options:  
 --help  Show this message and exit.
```

```
Usage: settle show [OPTIONS]  
  
 Shows all of your open transactions / groups along with IDs  
  
Options:  
 --email TEXT  
 -t, --transactions  
 -g, --groups  
 --help              Show this message and exit.

```

```
Usage: settle sign [OPTIONS] TRANSACTION_ID KEY_PATH  
  
 Signs a transaction  
  
Options:  
 --email TEXT  
 --password TEXT  
 --help           Show this message and exit.

```

```
Usage: settle verify [OPTIONS]  
  
 Will verify a transaction if given a transaction ID or an entire group if  
 given a group ID  
  
Options:  
 -t, --transactions  
 -g, --groups  
 --help              Show this message and exit.
```

```
Usage: settle new-group [OPTIONS]  

	Creates a new group

Options:  
 --name TEXT  
 --password TEXT  
 --help           Show this message and exit.
 ```

```
Usage: settle join [OPTIONS] GROUP_ID  
  
 Joins a group given an ID  
  
Options:  
 --email TEXT  
 --password TEXT  
 --group_password TEXT  
 --help                 Show this message and exit.
```

```
Usage: settle simplify [OPTIONS] GROUP_ID  
  
 Simplifies debt of a group  
  
Options:  
 --password TEXT  
 --help           Show this message and exit.
```

```
Usage: settle new-transaction [OPTIONS]  
  
 Generates a new transaction  
  
Options:  
 --dest_email TEXT  
 --amount TEXT  
 --reference TEXT  
 -g, --group TEXT  
 --email TEXT  
 --password TEXT  
 --help             Show this message and exit.
```

This text should also be displayed when the `--help` flag is called after any of the commands.  