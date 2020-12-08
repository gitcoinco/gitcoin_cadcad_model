from sim.model.logic import *

partial_state_update_blocks = [
    {
        'label': 'Append new edges to the network',
        'policies': {
            'new_contribution': p_new_contribution
        },
        'variables': {
            # 'network': s_append_edges,
            'contributions': s_append_contribution
        },
    },
    {
        'label': 'Quadratic Funding',
        'policies': {
            'quadratic_match': p_quadratic_match
        },
        'variables': {
            'quadratic_match_per_grant': s_quadratic_match_per_grant,
            'quadratic_funding_per_grant': s_quadratic_funding_per_grant,
            'quadratic_total_funding': s_quadratic_total_funding,
            'quadratic_total_match': s_quadratic_total_match

        }
    },
    {
        'label': 'Simple Quadratic Funding',
        'policies': {
            'simple_quadratic_match': p_simple_quadratic_match
        },
        'variables': {
            'simple_quadratic_match_per_grant': s_simple_quadratic_match_per_grant,
            'simple_quadratic_funding_per_grant': s_simple_quadratic_funding_per_grant,
            'simple_quadratic_total_funding': s_simple_quadratic_total_funding,
            'simple_quadratic_total_match': s_simple_quadratic_total_match

        }
    },
]