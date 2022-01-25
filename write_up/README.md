
# Analysis
---
## Project Outline 
A project to help groups of people manage money using RSA secured transactions and a computer app.

Features
+ Cryptographically signed transactions => security
+ Computer Interface
+ Client-Server Database
+ Settle your group's debts in the fewest number of transactions 

Non-Features
+ None of the user's money is ever put into the app. This is simply a tracker, you cannot settle debts through the app

## Background to the Problem
A common problem for many young people is that of money. More specifically, keeping track of who owes who how much money in a group of friends. Arguments about how much money is owed, and whether or not people have been remunerated are commonplace. This project aims to solve this problem through the use of an immutable ledger, made up of cryptographically signed transactions. When you agree to lend someone money, you both put the transaction on the blockchain, agreeing that it has, in fact, happened. When you receive what you owe, you mark the debt as paid. Like this, there can be no arguments - it exists as public knowledge.

## The End User
The end user that I had in mind is the friend who inspired this project. I think he fits perfectly within the target market - 13-18 years old, fairly sociable, not too technologically minded, and just wants an easy way to keep track of his transactions in his group of friends. 

My interviewee was keen to point out that people may abuse this system. They may just use it to rack up debt, and then never pay anyone back. He wanted to know if there was a way that I could stop this occurring. To this I replied no, not really. They can do the same thing without the app. It is your decision whether or not to lend to them. With the app however you can see exactly how much they've taken. It does however assume that people are willing to pay up. It is up to the user to deal with the eventuality that they don't.

Another problem that he identified was that of chains of debt. He (rightly) pointed out that if you owe people who owe people, its sometimes easier to cut out the middle man and turn two discreet transactions into one smaller one. This idea naturally extends to a group of friends, who may all have varying levels of debt between them. Thus, instead of making the group do a large number of transactions with money going back and forth frequently between the same hands, I will aim to let a group settle in the easiest way possible.

A valid concern with this plan is the fact that some may end up owing people they didn't before the simplification. Consider a simple case where A owes B £10, and B owes C £10. Two transactions could be reduced to 1, if A were to pay C directly. However, in a larger group, people may not like giving money to people who they do not directly owe on the will of my program. Hence, an impotant constraint is that no one owes someone that they didn't owe before settling occured (see image below.)

![[abc_debt.png]]

The final main worry that my interviewee brought up was that of guaranteed security. I had talked to him when I had the idea for this project, before I had learned about asymmetric encryption and cryptographic signatures. He wanted to know how a transaction coming from him could be verified as his, and no one else could pretend that they are, say, owed lots of money. He also didn't trust me, and said that if our group of friends started using this product, he would suspect that I would "code away my debts"

In order to convince my friends that I could not change their debts, I aim to implement RSA in as secure a way as I can manage in Python3 ^[There are, of course, still side channel vulnerabilities due to the way that Python3 stores number]. This would then be used to sign every transaction that goes through with the signatures of those who are involved. These transactions are then verified by the server before being added to the ledger. Like this, no one can pretend to be someone else, and any transactions that are in the ledger can be verified at any time. 


## High Level Objectives for the Solution

Having had my discussion with my user, there are immediately some obvious high level objectives. I have no doubt that during development, many secondary objectives will arise. 

1) An RSA implementation that will allow the signing, and verification, of transactions
2) A server-side component of the application which can verify and store transactions
3) A client-side component of the application that will have a user interface and allow the adding of transactions, viewing your debts, and editing user information
4) A way to settle the debts of the group in as few as possible (heuristically speaking) monetary transfers
5) A database that should be able to store user information, as well as transaction information
6) The user should be able to interact with the program through a simple GUI

## Low Level Requirements
==Pull from unittests==


## Research of existing solutions

Currently on the market, there are a few products similar to that which I am proposing. Having surveyed a few options, I decided to look at Evenfy and Splitwise in more detail.

Both work on the same premise that I have outlined: an intuitive way to track who owes who in a group.

This is all accurate at time of writing, however new updates since may 

### Evenfy
Evenfy is an app that does exactly what I set out to achieve. It mainly focuses on group expenses, and can be accessed from a computer.

It has an interesting feature in that it allows for temporary groups to be created in order to track short term expenses, such as over the course of an event. Evenfy tries to learn about common expenses, and suggests who pays over time. This may be useful if you rent a house with a few others, is what Evenfy say.

Evenfy will also calculate the easiest way to settle the group; that is, ensure that everyone's debt goes to 0. This is an integral part of keeping an expense tracking app usable in my opinion, and in the app's reviews, users seem to agree. 

![[evenfy_ui.png]]

Evenfy also allows for a group to settle debts easily. This feature will be discussed more in the next product evaluation, as an identical feature appears there.

Evenfy is free to use for the first 6 months, but then requires monthly subscription of 99 cents if you want to track more than 10 expenses per month.

### Splitwise
Splitwise is similar to Evenfy in many ways. It allows the easy splitting of bills (by percentage or equally), and keeps track of who owes whom within the group. 

![[splitwise_ui.png]]

After an account is created, you can create a group of people. Splitwise will then track all expenses in this group. Expenses can be referenced, and you can see at a glance exactly how much you owe. 

In comparison with Evenfy, the overall experience and featureset is similar. Both are well put together and include features that I think are unecessary for my target market. I do prefer Splitwise's UI slightly: it is easier on the eyes, and slightly less cluttered. Both have an excellent UX.

In terms of flaws, Splitwise requires a £2.99 per month subscription to unlock every feature (most core features are free to use). This is, in my opinion, better than Evenfy's payment model. However, the point is moot as I will not be charging for the use of this project.

The interesting part of these apps is in the debt simplification process. Since neither are open source, one cannot know for sure how the debt simplification is done. However, after much investigation, I found a few possible options.

==Add another research==

---
### Givers and Receivers

This, I believe, is the less likely of the two possible approaches, because it reduces down to a decision theory problem which is NP-Complete. It also takes a few passes of the data to get there. It is not particularly efficient. The steps are as follows

1) Calculate the net flow of each node
2) Categorize nodes into 'givers' (those who overall owe money) and 'receivers' (those who are overall owed), and those who owe/are owed nothing.
3) Settle any '1-1 transactions', where one 'giver' can completely remunerate a 'receiver'.
4) Settle any transactions where a receiver is owed a perfect subset of givers money (i.e. a receiver who is owed £5 could be settled by two givers, with £3 and £2)
5) Settle any remaining transactions by splitting money from givers in a greedy fashion to receivers.

The 'NP-completeness' of the problem starts at stage 4, when lots of computation has already been done on the data.

Stage 1 reducing all the transaction from Person A -> Person B to a single number. This is then done for the whole group, and a weighted digraph is built, where edges represent money owed. A residual graph, wherein an edge in the opposite direction with a weight $\times = -1$ the inital weight is added.

A breadth-first-search, where each edge traversed from the current node (_u_) has its weight recorded (and summed when all edges from _u_ are explored) is required to obtain the flow of the graph. This gives a time complexity of $\mathcal O(|V| + |E|)$.

The second step can be done very efficiently, in $\mathcal O(logV)$ time if a mergesort is used to sort the nodes in descending order of money they have (assuming those owed have negative amounts of money). Then the list of nodes can be split into two subsets at the point where 0 would be inserted into the list (those with a net debt of 0 can be removed before splitting).

Step 3 could be done by walking through the sorted givers list. For each node _g_ in the givers list, you would walk down the receivers list (_r_ in receivers), settling any transactions where _g_[money] = r[money]. (Any nodes which are not 'filtered' in this way move to a new stage of processing). This would give a time complexity of $\mathcal O (G\cdot R)$ , where G is the number of 'givers,' and R is the number of 'receivers'. This can be made much more efficient by using sorted lists, and remembering how far the receivers list was walked down in previous runs. 

In pseudocode

```
for giver in givers:
	for receiver in receivers:
		if giver.money > receiver.money:
			// giver has more money than any receiver in receivers
			giver passes filter
		else if giver.money < receiver.money:
		    // receiver is owed more money than any giver in givers has 
			receiver passes filter
		else:
			// giver and receiver have the same amount of money so a 1-1 can happen
			settle(giver, receiver)
			
```

Step 4 becomes a sum of subsets problem, and is NP-Complete, i.e. there is no algorithm which can solve this problem in quicker than exponential time. It is at this stage that this approach becomes infeasible for the real world, and thus, A better heuristic must be considered. 

Another problem with this approach is that it contradicts one of my initial high level requirements. It does not preserve any sense of who owes whom past step 1. Thus, it cannot guarantee that no one will owe anyone that they did not previously owe. 

For these two reasons, I shall elect to not use this method.

### Max Flow

The 'max flow' algrorithm takes a different approach. Instead of trying to restructure the graph to reduce the number of edges, max flow tries to optimise flow, so that fewer edges need to exist. This means the original structure of the graph is preserved in the sense that no new edges are formed - instead, redundant edges are removed.


==Entity Relationship Model==