import numpy as np
import networkx as nx


def aggregate_contributions(grant_contributions):
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


def get_totals_by_pair(contrib_dict):
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


def match_project(contribz, pair_totals, threshold):
    proj_total = 0
    for k1, v1 in contribz.items():
        for k2, v2 in contribz.items():
            if k2 > k1:
                # quadratic formula
                p = pair_totals[k1][k2]
                if p == 0:
                    continue
                else:
                    proj_total += (threshold + 1) * ((v1 * v2) ** 0.5) / p
    return np.real(proj_total)


def quadratic_match(G: nx.Graph,
                    threshold: float) -> dict:
    G = G.copy()
    raw_contributions = G.edges(data=True)

    grants_set = {n
                  for n, attrs
                  in G.nodes(data=True)
                  if attrs['type'] == 'grant'}

    contributions = []
    for contrib in raw_contributions:
        amount = contrib[2]['amount']
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
    pair_totals = get_totals_by_pair(contrib_dict)
    matches = {proj: match_project(contribz, pair_totals, threshold)
               for proj, contribz
               in contrib_dict.items()}
    return matches


def quadratic_funding(G: nx.Graph,
                      total_pot: float) -> dict:
    G = G.copy()
    grants = {label
              for label, node in G.nodes(data=True)
              if node['type'] == 'grant'}
    M = nx.get_node_attributes(G, 'match')

    total_match = sum(M.values())
    F = {}
    if total_match > total_pot:
        F = {g: total_pot * M[g] / total_match
             for g in grants}
    else:
        if total_match == 0:
            total_match = 1.0
        F = {g: M[g] + (1 + np.log(total_pot / total_match) / 100)
             for g in grants}
    return F


def total_quadratic_match(G: nx.Graph,
                          threshold: float) -> float:
    return sum(quadratic_match(G, threshold).values())
