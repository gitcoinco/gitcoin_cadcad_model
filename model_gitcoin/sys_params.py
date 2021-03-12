from model_gitcoin.parts.utils import load_contributions_sequence_from_excel
from model_gitcoin.parts.utils import load_contributions_sequence_from_csv
from collections import defaultdict
import os

CSV_PATH = 'data/model_data/data.tar.xz'
EXCEL_PATH = 'data/model_data/alternate_data.xls'
load_from_excel: str = os.environ.get('GITCOIN_LOAD_EXCEL')
    
if load_from_excel == 'yes':
    CONTRIBUTIONS_SEQUENCE = load_contributions_sequence_from_excel(EXCEL_PATH)
else:
    timesteps = os.environ.get('GITCOIN_TIMESTEPS')
    if timesteps == 'all':
        CONTRIBUTIONS_SEQUENCE: dict = load_contributions_sequence_from_csv(CSV_PATH, None)
    else:
        CONTRIBUTIONS_SEQUENCE: dict = load_contributions_sequence_from_csv(CSV_PATH, int(timesteps))

sys_params = {
    'contribution_sequence': [CONTRIBUTIONS_SEQUENCE],
    'trust_bonus_per_user': [defaultdict(lambda: 1.0)],
    'v_threshold': [1.0],
    'simple_threshold': [1.0],
    'total_pot': [450000]
}
