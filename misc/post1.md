# Complexity and Network Science for the resilence of Gitcoin Grants: announcing the BlockScience+Gitcoin collaboration

- Put a very high fps of the full movie here
- Create some suspense

## The history of sybil attacks

- Tell a nice story
- Put figure here of a sybil attack in a network science perspective
    - Orange intruder going into the blue giant component
    - Maybe we could take a inspiration from BrightID?
- Maybe we should announce collaboration with BSci and GC here? 
- Maybe we should have a suspense -> solution transition to the next section?

## A complex systems approach with cadCAD

- Tell how cadCAD helps generating knowledge about complex systems. Put examples. cite Aragon?
- Create a link with Gitcoin. Show understanding of how the Grants is a complex system

Although sybil attacks are hard to identify and tackle in a complex system, we have a open-source framework that is widely used on Web3 that is built specifically for the purpose of validating and informing decisions for those tough cyberphysical system. **cadCAD** is a Python library for simulations built originally by **BlockScience** which gives us tools for 

Some of the projects that uses cadCAD for empowering the design and validation process includes the Conviction Voting mechanism used by Aragon, which **--sell aragon here--**.

Another project, which **--maybe cite ICF and link with Gitcoin here?--**


## The Gitcoin Grants Network



- Create some written suspense
    - cadCAD allows you to consume the data from Gitcoin for generating a Dynamical Network for the Grants contributions
- Put full movie here
- Descriptive commentary

## What can we learn for Gitcoin with cadCAD?

- "cadCAD allows you to go beyond what beholds the eye"
- Put lots of data sciency figures here
    - Total quadratic funding over time
    - Share of the top 5 grants over time
    - (desirable) Gini coefficient for grant fundings over time
- "cadCAD allows you to AB test between different mechanisms so that you can compare different worlds"
    - Share of the top 5 grants without pairwise totals over time
    - (only if we have time and if approved) Gini coefficient for grant fundings over time in a capitalist matching
- There is a lot of science coming in over the next rounds. Maybe cite the collaboration between BlockScience and Gitcoin?


## You too can be a Gitcoin Grants Scientist: check out the Open Source repo!

- with cadCAD, anyone can simulate alternate scenarios!
- We've included a model where you can simulate your own custom scenario by editing a spreadsheet
    - Put image of one of the data sciency metrics here
    - Include directions
- Fork and star our repo!

Another aspect of cadCAD is that it goes beyond the past data: it also allows you to experiment with 


## Donate to the cadCAD Grant!!!

- Put a inspiring message here


---
---
-z Version

# Towards Computer Aided Governance of Gitcoin Grants

## Quadratic Funding

\comment{This thing is awesome}
Gitcoin Grants leverages a powerful algorithmic policy called quadratic funding to capture the preferences of a larger population by using a sum of square roots when computing the matching. This work was based off [cite cite cite].

\comment{this thing still has challenges}
While quadratic funding is very powerful, like any real world system it has weaknesses as well as strengths. Specifically, quadratic funding is sensitive to sybil attacks and collusion strategies. Furthermore, it has been observed to exhibit the Matthew Effect.[citations]

\comment{we can deal those challenges}
Rather than become disenchanted with quadratic funding, the Gitcoin team strives to operate a fair and transparent platform, including the ongoing maintainance of its algorithms.

## What does it mean to 'Govern' Gitcoin Grants?

The Gitcoin Grants platform doesn't directly control user decisions, it simply empowers them to coordinate in funding the projects the community deems most deserving of the match funds. The Quadratic Funding algorithm is the main 'resource allocation policy' but as it turns out, other algorithmic polices are at play. 

\comment{stuff gitcoin is already doing to manage these challenges!}
For example, there are sub algorithms which assign sybil scores and rewards for external identity verifications to defend against sybil attacks; there is a "pairwise (?)" algorithm which reduces the effect of collusion. 

\comment{why? // right to do so? }
More generally, the Gitcoin team reserves the rights to iterate upon the finer points of their matching algorithms in pursuit of their mandate:
> to provide a fair and transparent platform which empowers community donors to determine the allocation of a matching pool provided by sponsoring organizations. (?)

\comment{let's make this more emperical and more systematic}
In order to uphold this mandate the Gitcoin team must:
- identify specific instances of malicious activity
- indentify malicious strategies which game the algorithms to undermine the community goals
- identify misaligned incentives where honest behavior still results in undesirable system level outcomes
- propose alternative policies which address challenges identified
- test alternative policies to determine their most likely systemic impact
- communicate proposed changes and gain community buy-in for proposed policy changes

<!---
your comment goes here
and here
-->
## How Does One Do these things!?

This is accomplished which a complex systems approach, exemplied by a dynamic network model of the gitcoin CLR process. Fortunately, we have one of those!

The dynamic network model of gitcoin is comprised of 3 main components
1. A mathematical representation of 'trajectory' of a Gitcoin round including all of its grants, participants, and contributions.
2. A computational model of that 'dynamical system' implemented in cadCAD
3. Data from the real life Gitcoin system, representing specific historical actions taken by participants

Combining these three things, we have model of Gitcoin that allows us to run counterfactual analysis to test sensativity to various attacks, test out alternative policies, explore new metrics, or even do all three at the same time.

Much of this research is future work, but today we would like to share with you the first version of the gitcoin cadCAD model and invite you to follow our repo as we continue to flesh out new experiments, analyze new data, and support the gitcoin team in their quest for a fair and transparent way to distribute matching funds.