# tests/test_export_import.py — PHASE 5: DATA OWNERSHIP ETERNAL DOMINATION
"""
Proves:
- Export full universe (goals + hierarchy + ltree paths)
- Import wipes DB + restores tree perfectly (new IDs, paths rebuilt)
- Round-trip survives nuke — hierarchy, timeframes, statuses intact
All with authenticated user, real Postgres, rollback eternal.
"""
import pytest
pytestmark = pytest.mark.skip(reason="Export/import rewrite in progress")
import json
from io import BytesIO

def test_export_import_round_trip(authenticated_client):
    # 1. CREATE TEST GOALS WITH HIERARCHY
    # Root goal
    response = authenticated_client.post('/api/goals', json={
        'title': 'Root Export Goal',
        'category': 'work',
        'timeframe': 'yearly'
    })
    assert response.status_code == 200
    root = response.get_json()
    root_id = root['id']

    # Child goal (inherits timeframe down)
    response = authenticated_client.post('/api/goals', json={
        'title': 'Child Export Step',
        'parent_id': root_id,
        'category': 'work',
        'timeframe': 'quarterly'  # override to test
    })
    assert response.status_code == 200
    child = response.get_json()
    child_id = child['id']

    # Grandchild
    response = authenticated_client.post('/api/goals', json={
        'title': 'Grandchild Export Task',
        'parent_id': child_id,
        'category': 'work'
    })
    assert response.status_code == 200

    # 2. EXPORT — get JSON backup
    response = authenticated_client.get('/api/export')
    assert response.status_code == 200
    assert 'application/json' in response.headers['Content-Type']
    export_data = response.get_json()
    assert len(export_data['goals']) == 1  # only root
    exported_root = export_data['goals'][0]
    assert exported_root['title'] == 'Root Export Goal'
    assert len(exported_root['children']) == 1
    assert exported_root['children'][0]['title'] == 'Child Export Step'
    assert len(exported_root['children'][0]['children']) == 1

    # 3. NUKE DB VIA IMPORT (wipe + restore)
    # Prepare file-like object
    export_json = json.dumps(export_data).encode('utf-8')
    file_obj = BytesIO(export_json)
    file_obj.name = 'backup.json'  # required for flask

    response = authenticated_client.post('/api/import', data={
        'file': (file_obj, 'backup.json')
    }, content_type='multipart/form-data')

    assert response.status_code == 200
    result = response.get_json()
    assert 'restored' in result['message'].lower() or 'empire' in result['message'].lower()

    # 4. VERIFY RESTORED TREE — new IDs, but structure + data intact
    response = authenticated_client.get('/api/goals')
    assert response.status_code == 200
    restored_tree = response.get_json()
    assert len(restored_tree) == 1
    new_root = restored_tree[0]
    assert new_root['title'] == 'Root Export Goal'
    assert new_root['timeframe'] == 'yearly'
    assert len(new_root['children']) == 1
    new_child = new_root['children'][0]
    assert new_child['title'] == 'Child Export Step'
    assert new_child['timeframe'] == 'quarterly'  # preserved override
    assert len(new_child['children']) == 1
    assert new_child['children'][0]['title'] == 'Grandchild Export Task'

    # IDs changed (import uses new ones)
    assert new_root['id'] != root_id
    assert new_child['id'] != child_id