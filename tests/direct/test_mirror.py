from conftest import CONTRACT
import json


FACTORS = [
    'Documented severity of the incident',
    'Prior warnings on the account',
    'Measured customer impact',
]
OUTCOMES = ['APPROVE', 'DENY']


def opened(vm, deploy, owner, auditor):
    vm.sender = owner
    contract = deploy(CONTRACT)
    contract.register(
        'pair-7', '0x' + auditor.hex(), 'Paired access decisions',
        'https://policy.example/access', 'Declared region of the applicant', FACTORS, OUTCOMES,
    )
    return contract


def mock_sources(vm):
    vm.mock_web(r'policy\.example', {'status': 200, 'body': 'Decisions use severity, warnings, and impact. Region is irrelevant.'})
    vm.mock_web(r'left\.example', {'status': 200, 'body': 'Region North. Severity low. No warnings. Impact 2.'})
    vm.mock_web(r'right\.example', {'status': 200, 'body': 'Region South. Severity low. No warnings. Impact 2.'})


def mock_result(vm, different=None, justification='UNSUPPORTED', axis=True):
    different = different or []
    same = [index for index in range(len(FACTORS)) if index not in different]
    vm.mock_llm(
        r'.*CounterfactualMirror paired decision inspection.*',
        json.dumps({
            'protected_axis_differs': axis,
            'same_indexes': same,
            'different_indexes': different,
            'divergence_justification': justification,
        }),
    )


def inspect(contract, left='APPROVE', right='DENY'):
    contract.inspect_pair('pair-7', 'https://left.example/case', left, 'https://right.example/case', right)


def test_comparable_unsupported_split_is_disparate(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = opened(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    mock_sources(direct_vm)
    mock_result(direct_vm)
    inspect(contract)
    row = contract.get_mirror('pair-7')
    assert row['state'] == 'DISPARATE'
    assert row['same_indexes'] == [0, 1, 2]
    assert len(row['digests']) == 3


def test_equal_outcomes_produce_parity(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = opened(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    mock_sources(direct_vm)
    mock_result(direct_vm, justification='INAPPLICABLE')
    inspect(contract, 'APPROVE', 'APPROVE')
    assert contract.get_mirror('pair-7')['state'] == 'PARITY'


def test_material_difference_blocks_comparison(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = opened(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    mock_sources(direct_vm)
    mock_result(direct_vm, different=[2], justification='SUPPORTED')
    inspect(contract)
    assert contract.get_mirror('pair-7')['state'] == 'NOT_COMPARABLE'


def test_only_designated_auditor_can_inspect(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = opened(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_charlie
    mock_sources(direct_vm)
    mock_result(direct_vm)
    with direct_vm.expect_revert('designated auditor'):
        inspect(contract)


def test_validator_rejects_forged_factor_partition(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = opened(direct_vm, direct_deploy, direct_alice, direct_bob)
    mock_sources(direct_vm)
    mock_result(direct_vm)
    mirror = contract.mirrors['PAIR-7']
    result = contract._inspect(mirror, 'https://left.example/case', 'https://right.example/case', 'APPROVE', 'DENY')
    assert direct_vm.run_validator(leader_result=result) is True
    forged = dict(result)
    forged['different_indexes'] = [2]
    forged['same_indexes'] = [0, 1]
    assert direct_vm.run_validator(leader_result=forged) is False


def test_duplicate_id_and_replay_fail(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = opened(direct_vm, direct_deploy, direct_alice, direct_bob)
    with direct_vm.expect_revert('unique mirror id'):
        contract.register('pair-7', '0x' + direct_bob.hex(), 'Duplicate pair', 'https://policy.example/access', 'Region', FACTORS, OUTCOMES)
    direct_vm.sender = direct_bob
    mock_sources(direct_vm)
    mock_result(direct_vm)
    inspect(contract)
    with direct_vm.expect_revert('already inspected'):
        inspect(contract)
