from utils import load_contributions_sequence_from_excel
from utils import load_contributions_sequence
from collections import defaultdict
import os

if os.environ.get('GITCOIN_LOAD_EXCEL') == 'yes':
    CONTRIBUTIONS_SEQUENCE = load_contributions_sequence_from_excel('../data/alternate_data.xls')
else:
    CONTRIBUTIONS_SEQUENCE: dict = load_contributions_sequence(100)

sys_params = {
    'contribution_sequence': [CONTRIBUTIONS_SEQUENCE],
    'trust_bonus_per_user': [defaultdict(lambda: 1.0)],
    'v_threshold': [0.3],
    'simple_threshold': [0.3],
    'total_pot': [450000]
}