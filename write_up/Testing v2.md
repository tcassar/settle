# Testing
## Re-listed Low Level Requirements
The list of requirements low level requirements, identical to that in the Analysis section. 

#### RSA Implementation (A)
 1) A reliable interface to a hashing module
 
 2) RSA Key Handling:
	 1) Be able to load RSA public/private keys in PEM format from files / STDIN
	 2) Be able to validate the format of these keys
	 3) Be able to parse these keys extracting all necessary numbers for RSA decryption
 
 3) Signing/Verification
	 1) Have a valid RSA encryption scheme (encryption with public key)
	 2) Have a valid RSA decryption scheme (decryption with private key)
	 3) Have a valid RSA signing (sig) scheme (signing with private key)
	 4) Have a valid RSA signature verification (verif) scheme (verify with public key)
 
 4) Object Signing
	 1) Algorithm to convert an object to a hash in a reproducible way, minimising the chance of hash collisions
	 2) Ability to sign a class of object with RSA sig scheme
	 3) Ability to verify a signed object with RSA verif scheme, raising an error if signature is invalid 

#### Debt Simplification (B)
1) A reliable digraph structure, with operations to `transactions.graph.GenericDigraph`
	1) Get the nodes in the graph `nodes()`
	2) Check if an edge exists between two nodes
	3) Nodes can be added
	4) Nodes can be removed
	5) Edges can be added
	6) Edges can be removed
	7) Neighbours of a node should be easily accessed (neighbours for the purposes of a breadth first search)

2) A reliable flow graph structure
	1) All of the operations listed in B.1.1
	2)  Adding an edge should have different functionality: edge should be able to be added with a capacity, and edges should have a notion of flow and unused capacity
	3) Be able to return neighbours of nodes in the residual graph (i.e. edges, including residual edges, that have unused capacity)
	4) A way to get the bottleneck value of a path, given a path of nodes

3) A reliable recursive BFS that works on flow graphs

4) Implementation of Edmonds-Karp
	1) Way to find shortest augmenting path between two nodes
	2) Way to find bottleneck value of a path
	3) Finding max flow along a flow graph from source node to sink node

5) Simplifying an entire graph using Edmonds Karp, using the method laid out in [[#Settling a graph using a Max Flow algorithm]]. 

6) Be able to convert a list of valid transactions into a flow graph 

7) Be able to convert a flow graph into a list of transactions, signed by the server 

8) Be able to simplify a group of transactions, having each transaction individually verified before settling

#### Client / Server Structure (C)
1) The server should be accessible to the client via a REST API
2) The client should be relatively thin, only dealing with input from user and handling error 400 and 500 codes gracefully.
3) The client should have a clear, easy to use command line interface


#### 'Integrated' requriements for how the end system should behave (D)
1) Ensuring the validity of transactions
	1) If a transaction is tampered with in the database, it should be classed as unverified
    2) A user should not be able to sign an already signed transaction
    3) A user should not be able to sign a transaction where they are not one of the listed members
    4) A user should not be able to sign a transaction with a key that is not associated to their account
    5) A user should not be able to sign a transaction without entering their password correctly
    6) Every time a transaction is pulled from the database and sent to the user, it should be verified by the server using the RSA sig/verif scheme from section A
    8) A user should not be able to link a transaction to a group which either party is not a part of

2) Ensuring that the debt simplification feature works
	1) All transactions in the group being settled should be verified upon being pulled from the database
	2) It should not be possible to simplify a group if there are unverified transactions in the group
	3) If the transaction structure of the group does not change, the user should be notified
	4) The simplification should accurately simplify a system of debts such that no one is owed / owes a different amount of money after simplification
	5) The simplifying process should result in unverified transactions being produced, able to be signed by the user

3) Ancilliary features
	1) Users should be able to register for an account, providing name, email, password and a PEM formatted private key
	2) Users should be able to create transactions where they are the party owing money; these transactions should be created as unsigned
	3) Users should be able to create a group with a name and password
	4) Users should be able to join a group by group ID
	6) Users should be able to mark a transaction as settled; transactions should only be marked as settled when both parties involved mark the transaction as settled
	7) Users should be able to see which groups they are a member of
	8) Users should be able to see all of their open transactions.
	9) Users should be able to see all of the open transactions in a group (whether or not they are part of the group)
	10) Users should be able to see the public key information of any user on the system
	11) Users should be able to see individual transactions by passing in a transaction ID


#### Database Architecture (E)
1) User information
	1) User ID
	2) Contact info
	3) A hash of the user's password 
	4) Associated Groups
	5) Public Key (provisions for one or more)
2) Transaction Information
	1) Transaction ID
	2) Payee
	3) Recipient
	4) Transaction reference
	5) Amount (£)
	6) Payee's signature
	7) Recipient's signature
	8) Whether or not transaction has been settled
3)  Group information
	1) Group name
	2) Group password
	3) People in the group
	4) Transactions in the group


## Unit Test Framework
To demonstrate the effectiveness and completeness of sections A & B, I will provide my unit testing framework. I approaced implementation from a test-driven development perspective, and thus all of these tests were written before the code they run was implemented. 

This has led to the creation of an extensive, robust framework of tests, which effectively shows the extent to which I have completed sections A and B of my project.

The test harness has ~80% coverage on the `transactions`. `simplify` and `crypto` modules, with the crypto module having >90% coverage.

Below is a report of my tests running generated by my IDE, as well as a table linking individual unit tests to requirements from sections A and B. 

The unit tests are provided at the end of this section. 

(Note - the slightly long time that these tests took to run can be attributed to the drawing of graphs. I used the `graphviz` library to dynamically generate pictures of graphs of the debt that my algorithm was simplifying. Some of these are included below.)
![[Pasted image 20220321000032.png]]
![[Pasted image 20220321000057.png]]
![[Pasted image 20220321000126.png]]
![[Pasted image 20220321000146.png]]
![[Pasted image 20220321000210.png]]
![[Pasted image 20220321000325.png]]
![[Pasted image 20220321000346.png]]
![[Pasted image 20220321000412.png]]


![[test plan.png]]

 ### Proof of simplification algorithm correctness (B5)
 In the analysis section, I provided a hand-trace of the expected graph structures involved in settling a system of debts. Having done this hand tracing, I decided to use the same graph to test my algorithm. 
 
 Using the `graphviz` library I was able to generate before and after representations of the flow graphs used to simplify the system of debt it was fed. Here is my initial structure compared to the expected structure

**Expected**
![[main settle eg.png|500]]
**Generated**
![[pre_settle0.svg]]
Since this is debug output, IDs are displayed instead of names and residual edges and flows are shown. Here, red edges can be ignored, and you can take the debt along the edge to equal the capacity of the edge.

Though the identifiers are different, the generated graph is in the form of the expected graph

**Expected outcome**
![[correct settled.png|300]]

**Generated outcome**
![[settled0.svg|200]]

It is clear from these diagrams that the settling process has worked as expected, matching up perfectly with the hand-traced data. The same results are shown in the CLI of the technical solution

The first call`settle verify -g 11` returns all unsettled transactions stored by the database, and checks whether or not their signatures are valid. In this case, all signatures are valid and thus the group can be simplified. Transactions of the form of the graphs above are found in the group.

The second call is to `settle simplify 11`. This indicates to the server that group 11 should be simplified. The group's password has been entered correctly and thus simplification can occur.

The simplification process will then verify each transaction once more, and build a flow graph representation of the system of debts. My algorithm based on Edmonds-Karp is then run, and a single new transaction is generated. Again, this new transaction is in the form of the graphs above. proving the effectiveness of the solution

![[Pasted image 20220322170900.png]]

The transaction that is generated is marked as unverified. This is because the sever does not have access to the private keys of the users. If the server held private keys, it would not be a convincing security solution to say the least!

