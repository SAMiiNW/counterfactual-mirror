import json
import re
import time
from pathlib import Path

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet
from genlayer_py.types import TransactionStatus


ROOT = Path(__file__).parents[1]
ENV = (ROOT.parents[3] / 'accounts.env').read_text()
DEPLOYMENT = json.loads((ROOT / 'deployment.json').read_text())
ADDRESS = DEPLOYMENT['contractAddress']
COMMIT = DEPLOYMENT['sourceCommit']


def account(number):
    key = re.search(rf'^ACCOUNT_{number}_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)', ENV, re.M).group(1).strip()
    return create_account(account_private_key=key)


def client(number):
    return create_client(chain=studionet, account=account(number))


def write(number, name, args):
    active = client(number)
    tx = active.write_contract(address=ADDRESS, function_name=name, args=args)
    print(name + '_tx=' + str(tx), flush=True)
    receipt = active.wait_for_transaction_receipt(
        transaction_hash=tx,
        status=TransactionStatus.FINALIZED,
        retries=180,
        interval=5000,
        full_transaction=True,
    )
    leader = (receipt.get('consensus_data', {}).get('leader_receipt') or [{}])[0]
    assert receipt.get('result_name') == 'MAJORITY_AGREE'
    assert leader.get('execution_result') == 'SUCCESS'
    return str(tx)


base = f'https://raw.githubusercontent.com/SAMiiNW/counterfactual-mirror/{COMMIT}/evidence'
mirror_id = 'PAIR-' + str(int(time.time()))
factors = [
    'Documented severity of the incident',
    'Prior warnings on the account',
    'Measured customer impact',
]
transactions = {}
transactions['register'] = write(1, 'register', [
    mirror_id,
    account(2).address,
    'Paired access decisions',
    base + '/policy.md',
    'Declared operating region of the applicant',
    factors,
    ['APPROVE', 'DENY'],
])
transactions['inspect'] = write(2, 'inspect_pair', [
    mirror_id,
    base + '/left-case.md',
    'APPROVE',
    base + '/right-case.md',
    'DENY',
])
state = client(1).read_contract(address=ADDRESS, function_name='get_mirror', args=[mirror_id])
assert state['state'] == 'DISPARATE'
assert state['same_indexes'] == [0, 1, 2]
assert state['different_indexes'] == []
proof = {
    'mirrorId': mirror_id,
    'transactions': transactions,
    'state': state,
    'disclosure': 'The two cases, policy, and configured wallets are operator-controlled technical fixtures.',
}
(ROOT / 'evidence' / 'live-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps(proof, indent=2), flush=True)
