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
1) A reliable digraph structure, with operations to 
	1) Get the nodes in the graph 
	2) Check if an edge exists between two nodes
	3) Nodes can be added
	4) Nodes can be removed
	5) Edges can be added
	6) Edges can be removed
	7) Neighbours of a node should be easily accessed (neighbours for the purposes of a breadth first search)

2) A reliable flow graph structure
	1) All the operations listed in B.1.1
	2)  Adding an edge should have different functionality: edge should be able to be added with a capacity, and edges should have a notion of flow and unused capacity
	3) Be able to return neighbours of nodes in the residual graph (i.e. edges, including residual edges, that have unused capacity)
	4) A way to get the bottleneck value of a path, given a path of nodes

3) A reliable recursive BFS that works on flow graphs

4) Implementation of Edmonds-Karp
	1) Way to find the shortest augmenting path between two nodes
	2) Way to find bottleneck value of a path
	3) Finding max flow along a flow graph from source node to sink node

5) Simplifying an entire graph using Edmonds Karp, using the method laid out in [[#Settling a graph using a Max Flow algorithm]]. 

6) Be able to convert a list of valid transactions into a flow graph 

7) Be able to convert a flow graph into a list of transactions, signed by the server 

8) Be able to simplify a group of transactions, having each transaction individually verified before settling

#### Client / Server Structure (C)
1) The server should be accessible to the client via a REST API
2) The client should be relatively thin, only dealing with input from user and handling error 400 and 500 codes gracefully.
3) Client and Server should communicate over HTTP, using JSON as an information interchange format
4) The client should have a clear, easy to use command line interface


#### 'Integrated' requirements for how the end system should behave (D)
1) Ensuring the validity of transactions
	1) If a transaction is tampered with in the database, it should be classed as unverified
    2) A user should not be able to sign an already signed transaction
    3) A user should not be able to sign a transaction where they are not one of the listed members
    4) A user should not be able to sign a transaction with a key that is not associated to their account
    5) A user should not be able to sign a transaction without entering their password correctly
    6) Every time a transaction is pulled from the database and sent to the user, it should be verified by the server using the RSA sig/verif scheme from section A


2) Ensuring that the debt simplification feature works
	1) All transactions in the group being settled should be verified upon being pulled from the database
	2) It should not be possible to simplify a group if there are unverified transactions in the group
	3) If the transaction structure of the group does not change, the user should be notified
	4) The simplification should accurately simplify a system of debts such that no one is owed / owes a different amount of money after simplification
	5) The simplifying process should result in unverified transactions being produced, able to be signed by the user

3) Ancillary features
	1) Users should be able to register for an account, providing name, email, password and a PEM formatted private key
	2) Users should be able to create transactions where they are the party owing money; these transactions should be created as unsigned
	3) Users should be able to create a group with a name and password
	4) Users should be able to join a group by group ID
	5) Users should be able to mark a transaction as settled; transactions should only be marked as settled when both parties involved mark the transaction as settled
	6) Users should be able to see which groups they are a member of
	7) Users should be able to see all of their open transactions
	8) Users should be able to see all the open transactions in a group (whether they are part of the group)
	9) Users should be able to see the public key information of any user on the system
	10) Users should be able to see individual transactions by passing in a transaction ID


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
	5) Amount (??)
	6) Payee's signature
	7) Recipient's signature
	8) Whether transaction has been settled
3)  Group information
	1) Group name
	2) Group password
	3) People in the group
	4) Transactions in the group


## Unit Test Framework
To demonstrate the effectiveness and completeness of sections A & B, I will provide my unit testing framework. I approached implementation from a test-driven development perspective, and thus all of these tests were written before the code they run was implemented. 

This has led to the creation of an extensive, robust framework of tests, which effectively shows the extent to which I have completed sections A and B of my project.

The test harness has ~80% coverage on the `transactions`. `simplify` and `crypto` modules, with the crypto module having >90% coverage. This makes it hard to argue that my solution has not been adequately tested.

Below is a report of my tests running generated by my IDE, as well as a table linking individual unit tests to requirements from sections A and B. An interactive version of the file is included in the project files.

The unit tests are provided after the Evaluation. 

(Note - the slightly long time that these tests took to run can be attributed to the drawing of graphs. I used the `graphviz` library to dynamically generate pictures of graphs of the debt that my algorithm was simplifying. Some of these are included below.)
![[Pasted image 20220321000032.png]]
![[Pasted image 20220321000057.png]]
![[Pasted image 20220321000126.png]]
![[Pasted image 20220321000146.png]]
![[Pasted image 20220321000210.png]]
![[Pasted image 20220321000325.png]]
![[Pasted image 20220321000346.png]]
![[Pasted image 20220321000412.png]]

### Evidence of meeting Requirements - Section A & B

![[test plan.png]]

I appreciate this table may not show information about the individual tests. Every unit test I wrote has an informative docstring. Thus, refer to the code after the Evaluation for more clarification about the function of any unittest.

 ### Proof of simplification algorithm functionality (B5)
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

The first call `settle verify -g 11` returns all unsettled transactions stored by the database, and checks whether their signatures are valid. In this case, all signatures are valid and thus the group can be simplified. Transactions of the form of the graphs above are found in the group.

The second call is to `settle simplify 11`. This indicates to the server that group 11 should be simplified. The group's password has been entered correctly and thus simplification can occur.

The simplification process will then verify each transaction once more, and build a flow graph representation of the system of debts. My algorithm based on Edmonds-Karp is then run, and a single new transaction is generated. Again, this new transaction is in the form of the graphs above. proving the effectiveness of the solution

![[Pasted image 20220322170900.png]]

The transaction that is generated is marked as unverified. This is because the sever does not have access to the private keys of the users. If the server held user private keys, it would not be a convincing security solution to say the least!

This example fulfils requirements **D1.6**, **D2.1**, **D2.4**, and **D2.5**

A note on UI: the unverified flashes. This is hard to put in a screenshot.

Hence, I can show that every requirement in section A and B has been met.

### Evidence of Meeting Requirements - Section C
To show that my technical solution does in fact communicate over a REST API, I will show a simple get request made by the client and the corresponding logs produced by the server.

![[Pasted image 20220322181211.png]]
Here, it is possible to see that I have configured the API to run on the  `http://192.168.109.142:5000`. 

The `settle whois <email>` command returns a user's name and public/private keys given an email. This shows that the server is accessible to the client via a REST api. There is a visible `GET` request, followed by an endpoint of the API. This satisfies **C1**

To show the program fulfilling **C2**, (handling exception codes gracefully), here is what happens when you attempt to `whois` an email that does not exist.

![[Pasted image 20220322181619.png]]
The server has responded with a 404 error code to the client's GET request. On the client side, this has been detected and raised. It has then been handled gracefully before showing the client the type of error (a resource not found), and what that might be (invalid user info).

This type of behaviour is implemented for all errors that are expected to be raised during the programs normal operation. More severe errors, such as the warning when the user attempts to double sign a transaction, are coloured in red.
![[Pasted image 20220322182149.png]]

Above, it was shown that the client connects to the API using HTTP. This partially fulfills requirement **C3**. To fulfill it, it must be shown that JSON is used to communicate between client and server. Thus, I have briefly modified the `whois` command to dump the raw server response to STDOUT so that I can prove that this objective has been met (it was reverted after the test)
![[Pasted image 20220322182533.png]]
This clearly shows that JSON is the information interchange format being used. 

The screenshots of my CLI I have provided, I believe, effectively demonstrate a clear, easy to use command line interface. Thus, **C4** is also satisfied. Many more examples of output will be shown in the next section.

I can therefore say I have completed all of my requirements in Section C.

### Evidence of Meeting Requirements - Section D

**Ensuring the validity of transactions**

Upon inspecting transaction 13
![[Pasted image 20220322190103.png]]

Changing the amount owed in the database
![[Pasted image 20220322190207.png]]

(1287 -> 1490)

Querying again (here, the output of the old query is included first)
![[Pasted image 20220322190250.png]]

Hence, **D1.1** is shown to be fulfilled. 

Note that this transaction is signed. If I re-tamper with it to return the amount to 1287, it becomes valid again. I will show an attempt to re-sign it.
![[Pasted image 20220322190508.png]]
To demonstrate how the CLI handles invalid arguments, I attempted to sign an invalid transaction without a key. The CLI prompted me accordingly, and offered me the choice of using a `--help` flag. 

**D1.2** is thus fulfilled.

Below, I try to sign a transaction between `cassar.thomas.e@gmail.com` and `kezza@cherryactive.com` as a user on the account held by `mreymacia@gmail.com`. This is not allowed, fulfilling **D1.3**

![[Pasted image 20220322191019.png]]

Next, I try to sign the transaction as `cassar.thomas.e@gmail.com`, but with a different key to the one I registered my account with, fulfilling **D1.4**
![[Pasted image 20220322191109.png]]

I attempt to sign the transaction with my private key, but I mistype my password **D1.5**
![[Pasted image 20220322191224.png]]

**D1.6** was shown previously.



**D2.1**, **D2.4** and **D2.5** were shown previously.

To show that I have fulfilled **D2.2**, I will attempt to settle a group with unverified transactions
![[Pasted image 20220322192725.png]]

As aforementioned, the `Verified: False` messages blink. This is why they are not shown in this screenshot (evidence of blinking in video provided).

To show that I satisfy **D2.3**, **D3.2**, **D3.3**,  **D3.4**, and **D3.10** I will make a new group and add two users to it. I will then add a single transaction and attempt to settle. One transaction cannot be simplified, thus we should be warned that simplification cannot happen
![[Pasted image 20220322192441.png]]
**D3.3** and **D3.4** have been fulfilled

Making a transaction (thus fulfilling **D3.2** and **D3.10**)
![[Pasted image 20220322193201.png]]

It is initially unsigned - I then sign it with both users
![[Pasted image 20220322193437.png]]
It is now verified. Next, I try to settle group 12. Since it only one transaction, I should be alerted that no changes were made. 
![[Pasted image 20220322193540.png]]

Indeed, I am.

To show **D3.1**, I will register an account, first providing it with a public key. It should reject this. Then, I will then register the account with the correct key. I will confirm the creation of the account with the `settle whois` command, thus also fulfilling **D3.9**
![[Pasted image 20220322194638.png]]

Successful creation
![[Pasted image 20220322195418.png]]

To show fulfillment of **D3.5**, **D3.7**, and **D3.8**. I will find an open transaction and mark it as settled. It should no longer appear in a set of group debts after both parties mark it as settled, but should appear if only one party has marked it as settled.
![[Pasted image 20220322195903.png]]
I will now sign transaction 2 by both parties - this has already been documented and thus won't be shown again.

Showing group three (and fulfilling **D3.8**), we see two transactions. After one party marks it as settled, it is still classed as an open transaction. Once the second party has ticked it off it is counted as settled. Hence, it is no longer shown with the rest of the open group transactions.

![[Pasted image 20220322201225.png]]

This shows transactions 2 and 3 listed as unmarked until both parties have ticked transaction 2. In the final call to `verify`, only transaction 3 is shown. Hence, **D3.5** and **D3.7** have been met.

Evidence for **D3.6**:
![[Pasted image 20220322201629.png]]


### Evidence of Meeting Requirements - Section E
To show that I have implemented the database structure that I laid out in my requirements, I will screenshot the database tables, and briefly comment on which requirements each table fulfils.

Not only does this show the structure of the data being stored, it also proves that I am storing data as per my requirements.

**Transactions**
This table fulfills **E2.1 -> E2.8** in conjunction with the `pairs` table and the `keys` table. It also satisfies **E3.4**

![[Pasted image 20220322202710.png]]

**Pairs**

![[Pasted image 20220322201840.png]]
**Keys**
![[Pasted image 20220322201901.png]]

**Users**
The users table, along with the keys table above, fulfil requirements **E1.1 -> E1.5**
![[Pasted image 20220322201948.png]]

**Groups**
The final outstanding requirements in Section E are met by the `groups` table and `groups_link` table, meeting **E3.1 -> E3.3**
![[Pasted image 20220322202041.png]]

Hence, I have entirely fulfilled every requirement I outlined in Section E, and have thus completed my project entirely.


# Evaluation
I will evaluate my completed project by gaining the opinion of the end user that I talked in the Analysis phase. I plan to give him a demonstration of the project, and let him use the project for a week. I will then collect and reflect on his feedback. 

In the demo, I thought it to be important to directly address the main concerns that he originally highlighted. These were mainly centred around system administrators (me) altering the amount of money that people owe each other.

To put his mind at ease, I gave him a live demonstration of the tampering test I used to show that my system fulfilled requirement **D1.1**. He was extremely impressed with this and spent the next 5 minutes tampering with data in the database, and watching the previously verified transactions become unverified. 

Once he had convinced himself that public key cryptography works, we moved on to addressing his next concern - debt simplification. Again, I showed him the 'simplify debt' example that I used in my analysis, and we spent the next 10 minutes building graphs and watching them simplify down. 

During this, he became increasingly comfortable using the CLI. He told me he was a bit hesitant when he saw it - it looked like nothing he had ever used before. While playing with the security and debt simplification features of the app, it was quite interesting to see just how quickly he got used to it. He told me that a CLI was definitely a good choice for this, due to just how simple it is to get things done. 

However, he was not completely without criticism.

He reported, fairly, that it was slightly annoying to have to keep entering your email and password, especially when he had entered this information just one command before. 

He also said that he would like a way to see his closed transactions in a list view, not just accessing them by ID. 

Finally, he said that he was confused as to why he had to generate an OpenSSL RSA Private key himself and then feed it into the `settle register` command. In his opinion, a key generate command would have been helpful.

I think that these are entirely valid concerns, and would be where I go next if I were to continue to improve the project. 

I decided to look into how I would go about implementing the end user's suggestions.

The email / password remembering could be achieved relatively straightforwardly with the `click` library using the concept of `contexts`. This is most definitely something that is doable, and would do a lot to aid the overall user experience.

Similarly, it would be trivial to add use a binding to OpenSSL and have my client be able to generate an RSA private key through the CLI. This is just something I hadn't considered in my Analysis of the project, but would definitely add to the user experience.

Adding a view for closed transactions would be another command a modified SQL statement, and I would probably need to add query parsing to my API endpoints, so that I could keep my server processes almost identical (aside from writing the new statement and query parser). I would then be able to pull transactions either open or closed, fully with code that already exists.

However, I was on the whole extremely happy with his response. When I asked him on how good a fit my solution to his problem was, he told me that with his additions, it would be absolutely perfect. 

---

When considering the extent to which I met my own high level requirements, I am really quite pleased. While everything was planned and meticulously designed, I am still surprised at just how robust my end product is. 

### Individual Requirement Reflection

**An RSA implementation that will allow the signing, and verification, of transactions**

On the whole I have built a robust, functional implementation of RSA for this project, which effectively fulfils the aim of preventing tampering with transactions (as well as more menial things such as password hashing). If I were to do this project again, however, I would not have written the cryptography side of things in Python. 

Due to the way that Python stores numbers, it is impossible to rule out the possibility of side channel attacks. Similarly, I did not use a constant time algorithm for the modular exponentiation step of RSA. Thus, it would be possible for an attacker to use a timing attack to deduce the private exponent in a user's private key. 

I think in the context that I had intended the project to be used in, this is not currently a massively pressing issue. Knowing about it does mean, however, that I would like to protect against it even if it means learning a new programming language.

**A way to settle the debts of the group in as few as possible (heuristically speaking) monetary transfers**

I am most pleased with the debt simplification - I think that that is a genuinely useful idea, and I am happy that it works so well.  I did learn some interesting things about how the heuristic model behaved when I was experimenting with making graphs with my end user. 

I discovered that the algorithm that I implemented to simplify groups of debt works best on densely connected graphs as more augmenting paths can be found. This makes me wonder if there is a way to change how I search for augmenting paths in the flow graph to try and end up with longer chains of debt. 

The problem is that a path of $n + 1$ edges has a higher chance of a smaller bottleneck value than a path with $n$ edges, and could end up leading to the time complexity of the algorithm being dependent on flow. This would potentially make the algorithm less efficient.   

This is something that I would like to investigate more in the future. 

Another thing that I would like to test is adding cycle detection to the graph. I feel as though I could improve the performance of my heuristic if I simplified cycles before running any flow graph algorithms. However, this may worsen the time complexity of the process as a whole. This, it is another thing to experiment with. 

**A server-side component of the application which can verify transactions, and store / retrieve them from a database**

**A client-side component of the application that will have a simple user interface (CLI)**

![Pasted image 20220322190829.png](app://local/%2Fhome%2Ftcassar%2Fprojects%2Fsettle%2Fwrite_up%2Fimages%2FPasted%20image%2020220322190829.png?1647976109574)
A screenshot of the simple, easy to use CLI

The next two requirements can be addressed as one. I am very happy with the client-server model of the system, even though the client-server model was much more work than I imagined.  However, it is quite impressive to see communication across a network, even if it is currently a localhost network.

Having a thin client is particularly easy and effective as it means that, if more people were to adopt this solution and I were to set up a full-time server, this could be run on absolutely everything. 

As was discussed with the end user, there are certain improvements that I could make to the CLI. These are very much quality of life improvements, and the CLI that I provided was more than adequate at fulfilling all of my initial requirements

**A database that should be able to store user and transaction information**

Finally, I am happy with my database. However, as I became more comfortable with SQL during the project, having had absolutely no experience with it before, I realise that I have a redundant relationship in my database design. The transaction table references the keys table. Having learned about the join statement, I now see that this link is redundant and ought not to be there.

