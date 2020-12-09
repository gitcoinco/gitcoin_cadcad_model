# Gitcoin Analysis

This cadCAD model and notebook series is a collaboration between Gitcoin and BlockScience. A brief table of contents follows to explain the file structure of the various documents produced in this collaboration.

## Table of Contents

### Notebooks


<The current goal is to perform a EDA around the existing data for Gitcoin Grants, which have a graph-like structure.>

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