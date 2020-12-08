import numpy as np

def aggregate_contributions(grant_contributions):
    contrib_dict = {}
    for contrib in grant_contributions:
        contrib_tuple = tuple(contrib.values())
        user = contrib_tuple[0]
        proj = contrib_tuple[1]
        amount = contrib_tuple[2]
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


def simple_match_project(contribz, threshold):
    proj_total = 0
    for k1, v1 in contribz.items():
        for k2, v2 in contribz.items():
            if k2 > k1:
                proj_total += (threshold + 1) * ((v1 * v2) ** 0.5)
    return np.real(proj_total)


def p_new_contribution(params, substep, state_history, prev_state):
    timestep: int = prev_state['timestep']
    new_contribution: tuple = params['contribution_sequence'][timestep]
    return {'new_contribution': new_contribution}


def s_append_contribution(params, substep, state_history, prev_state, policy_input):
    contributions = prev_state['contributions'].copy()
    contributions.append(policy_input.get('new_contribution'))
    return ('contributions', contributions)


def s_append_edges(params, substep, state_history, prev_state, policy_input):
    # Dependences
    G = prev_state['network'].copy()
    contribution = policy_input['new_contribution']
    G.add_edge(contribution['contributor'], contribution['grant'])
    return ('network', G)


def p_quadratic_match(params, substep, state_history, prev_state):
    threshold = params['v_threshold']
    total_pot = params['total_pot']
    pair_totals = prev_state['pair_totals']
    contributions = prev_state['contributions']

    grants = {c['grant'] for c in contributions}
    contrib_dict = aggregate_contributions(contributions)
    pair_totals = get_totals_by_pair(contrib_dict)
    M = {proj: match_project(contribz, pair_totals, threshold)
         for proj, contribz in contrib_dict.items()}

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

    return {'quadratic_match_per_grant': M,
            'quadratic_funding_per_grant': F}


def s_quadratic_match_per_grant(params, substep, state_history, prev_state, policy_input):
    M = policy_input['quadratic_match_per_grant']
    return ('quadratic_match_per_grant', M)


def s_quadratic_funding_per_grant(params, substep, state_history, prev_state, policy_input):
    F = policy_input['quadratic_funding_per_grant']
    return ('quadratic_funding_per_grant', F)


def s_quadratic_total_match(params, substep, state_history, prev_state, policy_input):
    M = policy_input['quadratic_match_per_grant']
    return ('quadratic_total_match', sum(M.values()))


def s_quadratic_total_funding(params, substep, state_history, prev_state, policy_input):
    F = policy_input['quadratic_funding_per_grant']
    return ('quadratic_total_funding', sum(F.values()))


def p_simple_quadratic_match(params, substep, state_history, prev_state):
    threshold = params['simple_threshold']
    total_pot = params['total_pot']
    contributions = prev_state['contributions']

    grants = {c['grant'] for c in contributions}
    contrib_dict = aggregate_contributions(contributions)
    M = {proj: simple_match_project(contribz, threshold)
         for proj, contribz in contrib_dict.items()}

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

    return {'simple_quadratic_match_per_grant': M,
            'simple_quadratic_funding_per_grant': F}


def s_simple_quadratic_match_per_grant(params, substep, state_history, prev_state, policy_input):
    M = policy_input['simple_quadratic_match_per_grant']
    return ('simple_quadratic_match_per_grant', M)


def s_simple_quadratic_funding_per_grant(params, substep, state_history, prev_state, policy_input):
    F = policy_input['simple_quadratic_funding_per_grant']
    return ('simple_quadratic_funding_per_grant', F)


def s_simple_quadratic_total_match(params, substep, state_history, prev_state, policy_input):
    M = policy_input['simple_quadratic_match_per_grant']
    return ('simple_quadratic_total_match', sum(M.values()))


def s_simple_quadratic_total_funding(params, substep, state_history, prev_state, policy_input):
    F = policy_input['simple_quadratic_funding_per_grant']
    return ('simple_quadratic_total_funding', sum(F.values()))
