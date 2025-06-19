import json


def test_get_user_profile_me_unauthorized(client):
    """Test getting own profile without API key."""
    response = client.get('/api/users/me')
    assert response.status_code == 401


def test_get_user_profile_me_success(client, auth_headers, user):
    """Test getting own profile with API key."""
    response = client.get('/api/users/me', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['result'] is True
    assert data['user']['name'] == 'User@2'


def test_get_user_profile_not_found(client):
    """Test getting non-existent user profile."""
    response = client.get('/api/users/999')
    assert response.status_code == 404


def test_get_user_profile_success(client, user):
    """Test getting user profile."""
    response = client.get(f'/api/users/{user.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user']['name'] == 'user1'


def test_follow_user_unauthorized(client, second_user):
    """Test following user without API key."""
    response = client.post(f'/api/users/{second_user.id}/follow')
    assert response.status_code == 401


def test_follow_user_success(client, auth_headers, user, second_user):
    """Test following user with API key."""
    response = client.post(
        f'/api/users/{second_user.id}/follow',
        headers=auth_headers
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['result'] is True


def test_unfollow_user_success(client, auth_headers, user, second_user, follow_factory):
    """Test unfollowing user with API key."""
    response = client.post(
        f'/api/users/{second_user.id}/follow',
        headers=auth_headers
    )

    response = client.delete(
        f'/api/users/{second_user.id}/follow',
        headers=auth_headers
    )
    assert response.status_code == 204
