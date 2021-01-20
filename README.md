# Gitcoin Analysis

This cadCAD model and notebook series is a collaboration between Gitcoin and BlockScience. A brief table of contents follows to explain the file structure of the various documents produced in this collaboration.

* TOC {:toc}

## How to use

1. Install all requirements: `pip install -r requirements.txt`
2. Change the parameters on `env_config.py` so that it fits your use case.
3. Run the simulation through `python run_simulation.py` so that we generate the `model/data/simulation_result.pkl.gz` pickled file. 
	* Alternatively, you can just unzip the `model/data/simulation_result.tar.xz` file.
4. Perform any analytics on the generated data or use one of the available notebooks.

## Simulation Notebook

### Dynamic Network exploratory analysis 

Notebook: [dynamic_network.ipynb](dynamic_network.ipynb) - 

This notebook showcases the cadCAD networked model using raw CSV data

### Graph-based communites in Gitcoin

Notebook: [graph_communities.ipynb](graph_communities.ipynb)

This notebook contains visualizations of communites on Gitcoin

## Medium Articles
* [Towards Computer-Aided Governance of Gitcoin Grants](https://medium.com/block-science/towards-computer-aided-governance-of-gitcoin-grants-730de7bcdbef)
* [Colluding Communities or New Markets?](https://medium.com/block-science/colluding-communities-or-new-markets-f64194a1b754)
### Quadratic Funding

Quadratic Voting captured the hearts of the web3 space after being re-introduced by the [Radical xChange movement](https://www.radicalxchange.org/). Gitcoin builds on the same principle by leveraging a powerful algorithmic policy called [Quadratic Funding (QF)](https://wtfisqf.com/?grant=&grant=&grant=&grant=&match=1000) to allocate sponsor funds via matching community donations to grants submitted through the Gitcoin Grants program. The purpose of this form of grant matching is to allocate sponsor funding via a community preference signal by capturing not just the depth of donations ($ amount donated), but also the breadth of the donation base (# people who donated). The outcome is that grants that are supported by many people with small donations would receive relatively larger matching than grants supported by few donations of larger amounts. In effect, **Quadratic Funding aims to boost the influence of people over plutocracy.**

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
In order to reperform this code, we recommend the researcher use the following link https://www.anaconda.com/products/individual to download Python 3.7. To install the specific version of cadCAD this repository was built with, run the following code: ```pip install -r requirements.txt'''

Check out the cadCAD forum for more information about installing and using cadCAD
