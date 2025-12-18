# tests/test_auth.py — AUTH + @login_required PROTECTION DOMINATION
"""
Proves:
- Unauthenticated → redirect containing /login (with possible ?next)
- Authenticated → 200 on protected routes
- Logout → flash message + redirect to login
- After logout → protected routes redirect again
All with real routes, real redirects, rollback eternal.
"""
def test_login_required_protection(client):
    """Unauthenticated → 302 redirect containing /login (with possible ?next)"""
    protected = ['/goals', '/tasks', '/calendar', '/calendar/day/2025/12/18', '/api/goals']
    for route in protected:
        response = client.get(route, follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

def test_authenticated_access(authenticated_client):
    """Authenticated → 200 on protected routes"""
    protected = ['/goals', '/tasks', '/calendar', '/calendar/day/2025/12/18', '/api/goals']
    for route in protected:
        response = authenticated_client.get(route)
        assert response.status_code == 200

def test_logout(authenticated_client):
    """Logout → flash + redirect to login page"""
    response = authenticated_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Logged out' in response.data
    assert b'ENTER THE RING' in response.data  # confirms on login page

    # After logout, protected routes redirect again
    response = authenticated_client.get('/goals', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']