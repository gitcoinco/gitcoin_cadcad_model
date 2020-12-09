from collections import defaultdict

genesis_states = {
    # 'network': nx.DiGraph(),
    'contributions': [],
    # (N_user, N_user)
    'pair_totals': defaultdict(lambda: defaultdict(lambda: 0.0)),
    'quadratic_match': defaultdict(lambda: 0.0),  # (N_grant)
    'quadratic_funding_per_grant': defaultdict(lambda: 0.0),
    'quadratic_match_per_grant': defaultdict(lambda: 0.0),
    'quadratic_total_match': 0.0,
    'quadratic_total_funding': 0.0,
    'simple_quadratic_match': defaultdict(lambda: 0.0),  # (N_grant)
    'simple_quadratic_funding_per_grant': defaultdict(lambda: 0.0),
    'simple_quadratic_match_per_grant': defaultdict(lambda: 0.0),
    'simple_quadratic_total_match': 0.0,
    'simple_quadratic_total_funding': 0.0,
}