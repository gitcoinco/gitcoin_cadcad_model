# Gitcoin Analysis

This cadCAD model and notebook series is a collaboration between Gitcoin and BlockScience. A brief table of contents follows to explain the file structure of the various documents produced in this collaboration.

## Table of Contents
## 1. Supporting Documentation
* <link to medium and any other relevant text here >

## 2. Simulation Notebooks
* [dynamic_network.ipynb](dynamic_network.ipynb) - Network model using raw CSV data

## Gitcoin
## Towards Computer Aided Governance of Gitcoin Grants

### Quadratic Funding

Gitcoin Grants leverages a powerful algorithmic policy called quadratic funding to capture the preferences of a larger population by using a sum of square roots when computing the matching.

While quadratic funding is very powerful, like any real world system it has weaknesses as well as strengths. Specifically, quadratic funding is sensitive to sybil attacks and collusion strategies. Furthermore, it has been observed to exhibit the Matthew Effect.

Rather than become disenchanted with quadratic funding, the Gitcoin team strives to operate a fair and transparent platform, including the ongoing maintainance of its algorithms.

### What does it mean to 'Govern' Gitcoin Grants?

The Gitcoin Grants platform doesn't directly control user decisions, it simply empowers them to coordinate in funding the projects the community deems most deserving of the match funds. The Quadratic Funding algorithm is the main 'resource allocation policy' but as it turns out, other algorithmic polices are at play. 

For example, there are sub algorithms which assign sybil scores and rewards for external identity verifications to defend against sybil attacks; there is a "pairwise (?)" algorithm which reduces the effect of collusion. 

More generally, the Gitcoin team reserves the rights to iterate upon the finer points of their matching algorithms in pursuit of their mandate:
> to provide a fair and transparent platform which empowers community donors to determine the allocation of a matching pool provided by sponsoring organizations. (

In order to uphold this mandate the Gitcoin team must:
- identify specific instances of malicious activity
- indentify malicious strategies which game the algorithms to undermine the community goals
- identify misaligned incentives where honest behavior still results in undesirable system level outcomes
- propose alternative policies which address challenges identified
- test alternative policies to determine their most likely systemic impact
- communicate proposed changes and gain community buy-in for proposed policy changes


### How Does One Do these things!?

This is accomplished which a complex systems approach, exemplied by a dynamic network model of the gitcoin CLR process. Fortunately, we have one of those!

The dynamic network model of gitcoin is comprised of 3 main components
1. A mathematical representation of 'trajectory' of a Gitcoin round including all of its grants, participants, and contributions.
2. A computational model of that 'dynamical system' implemented in cadCAD
3. Data from the real life Gitcoin system, representing specific historical actions taken by participants

Combining these three things, we have model of Gitcoin that allows us to run counterfactual analysis to test sensativity to various attacks, test out alternative policies, explore new metrics, or even do all three at the same time.

Much of this research is future work, but today we would like to share with you the first version of the gitcoin cadCAD model and invite you to follow our repo as we continue to flesh out new experiments, analyze new data, and support the gitcoin team in their quest for a fair and transparent way to distribute matching funds.

## Background information & concepts addressed
### What does this cadCAD model do
In cyber-physical systems like international power grids, global flight networks, or socioeconomic community ecosystems, engineers model simulated replicas of their system, called digital twins. These models help to manage the complexity of systems that have trillions of data points and are constantly in flux. These simulations channel the information into pathways that allow humans to understand what is going on in their ecosystem at a high level, so they can intervene where and as appropriate. (Like hitting a breaker switch when a fault is cleared in a power system).

![img](https://i.imgur.com/kb4Tnh6.jpg)

Digital twins can be considered like a flight simulator, which can be used to run your system through a billion different "tests", varying one parameter at a time, to see what effects may throw your system out of balance. As engineers with public safety in mind, we must understand the tipping points of our systems, and ensure mechanisms are in place to push the system back towards balance if and when they enter their boundary conditions of safety.

## What is cadCAD?
cadCAD (complex adaptive dynamics Computer-Aided Design) is a python based modeling framework for research, validation, and Computer Aided Design of complex systems. Given a model of a complex system, cadCAD can simulate the impact that a set of actions might have on it. This helps users make informed, rigorously tested decisions on how best to modify or interact with the system in order to achieve their goals. cadCAD supports different system modeling approaches and can be easily integrated with common empirical data science workflows. Monte Carlo methods, A/B testing and parameter sweeping features are natively supported and optimized for.

cadCAD links:

https://community.cadcad.org/t/introduction-to-cadcad/15
https://community.cadcad.org/t/putting-cadcad-in-context/19
https://github.com/cadCAD-org/demos

### Model Reproducibility
In order to reperform this code, we recommend the researcher use the following link https://www.anaconda.com/products/individual to download Python 3.7. To install the specific version of cadCAD this repository was built with, run the following code: pip install cadCAD==0.4.23

Then run cd Aragon_Conviction_Voting to enter the repository. Finally, run jupyter notebook to open a notebook server to run the various notebooks in this repository.

Check out the cadCAD forum for more information about installing and using cadCAD