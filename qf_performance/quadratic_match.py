import numpy as np
import networkx as nx
from time import time
from collections import namedtuple

NewContribution = namedtuple('new_contribution', ['contributor', 'grant', 'amount'])

def aggregate_contributions(grant_contributions: list) -> dict:
    contrib_dict = {}
    for contrib in grant_contributions:
        contrib_tuple = tuple(*contrib.values())
        user = contrib_tuple[1]
        proj = contrib_tuple[2]
        amount = contrib_tuple[3]
        if proj not in contrib_dict:
            contrib_dict[proj] = {}
        contrib_dict[proj][user] = contrib_dict[proj].get(user, 0) + amount
    return contrib_dict


def get_totals_by_pair(contrib_dict: dict) -> dict:
    tot_overlap = {}

    # start pairwise match
    for _, contribz in contrib_dict.items():
        for k1, v1 in contribz.items():
            if k1 not in tot_overlap:
                tot_overlap[k1] = {}

            # pairwise matches to current round
            for k2, v2 in contribz.items():
                if k2 not in tot_overlap[k1]:
                    tot_overlap[k1][k2] = 0
                tot_overlap[k1][k2] += (v1 * v2) ** 0.5

    return tot_overlap


def match_project(contribz: dict, pair_totals: dict, threshold: float) -> float:
    proj_total: float = 0
    for k1, v1 in contribz.items():
        for k2, v2 in contribz.items():
            if k2 > k1:
                # quadratic formula
                p: float = pair_totals[k1][k2]
                if p == 0:
                    continue
                else:
                    proj_total += (threshold + 1) * ((v1 * v2) ** 0.5) / p
    return np.real(proj_total)


def quadratic_match(G: nx.Graph, threshold: float) -> dict:
    t1 = time()
    G = G.copy()
    raw_contributions = G.edges(data=True)

    grants_set = {n for n, attrs in G.nodes(data=True) if attrs["type"] == "grant"}

    contributions = []
    for contrib in raw_contributions:
        amount = contrib[2]["amount"]
        grant = contrib[1]
        if grant not in grants_set:
            grant = contrib[0]
            contributor = contrib[1]
        else:
            contributor = contrib[0]
        # {'grant': {match, user, grant, amount}}
        element = {grant: (None, contributor, grant, amount)}
        contributions.append(element)

    contrib_dict = aggregate_contributions(contributions)
    pt_t1 = time()
    pair_totals = get_totals_by_pair(contrib_dict)
    pt_t2 = time()
    matches = {
        proj: match_project(contribz, pair_totals, threshold)
        for proj, contribz in contrib_dict.items()
    }
    pt_t3 = time()
    pair_totals_time = pt_t2 - pt_t1
    match_vector_time = pt_t3 - pt_t2
    t2 = time()
    total_time = t2 - t1
    return {'total_time': total_time,
            'pair_totals_time': pair_totals_time,
            'match_vector_time': match_vector_time}


def update_pair_totals(G: nx.Graph,
                       P: dict,
                       new_contribution: NewContribution) -> dict:


    new_P = {}

    # P = P + dP for dicts
    for (k_1, v_1) in new_P.items():
        for (k_2, v_2) in v_2.items():
            P[k_1][k_2] += v_2

    return new_P


def iterative_quadratic_match(G: nx.Graph,
                              threshold: float, 
                              pair_wise_totals: dict,
                              new_contribution: NewContribution) -> dict:
    """
    new_contributions: (contribution, grant, amount)
    """
    t1 = time()
    G = G.copy()
    raw_contributions = G.edges(data=True)

    grants_set = {n for n, attrs in G.nodes(data=True) if attrs["type"] == "grant"}

    contributions = []
    for contrib in raw_contributions:
        amount = contrib[2]["amount"]
        grant = contrib[1]
        if grant not in grants_set:
            grant = contrib[0]
            contributor = contrib[1]
        else:
            contributor = contrib[0]
        # {'grant': {match, user, grant, amount}}
        element = {grant: (None, contributor, grant, amount)}
        contributions.append(element)

    contrib_dict = aggregate_contributions(contributions)
    pt_t1 = time()
    pair_totals = update_pair_totals(G, pair_wise_totals, new_contribution)
    pt_t2 = time()
    matches = {
        proj: match_project(contribz, pair_totals, threshold)
        for proj, contribz in contrib_dict.items()
    }
    pt_t3 = time()
    pair_totals_time = pt_t2 - pt_t1
    match_vector_time = pt_t3 - pt_t2
    t2 = time()
    total_time = t2 - t1
    return {'total_time': total_time,
            'pair_totals_time': pair_totals_time,
            'match_vector_time': match_vector_time}


def quadratic_funding(G: nx.Graph, total_pot: float) -> dict:
    G = G.copy()
    grants = {label for label, node in G.nodes(data=True) if node["type"] == "grant"}
    M = nx.get_node_attributes(G, "match")

    total_match = sum(M.values())
    F = {}
    if total_match > total_pot:
        F = {g: total_pot * M[g] / total_match for g in grants}
    else:
        if total_match == 0:
            total_match = 1.0
        F = {g: M[g] + (1 + np.log(total_pot / total_match) / 100) for g in grants}
    return F


def total_quadratic_match(G: nx.Graph, threshold: float) -> float:
    return sum(quadratic_match(G, threshold).values())


def partial_quadratic_match(G: nx.Graph, nodes: set, threshold: float) -> float:
    matches = quadratic_match(G, threshold)
    return sum(match for grant, match in matches.items() if grant in nodes)
