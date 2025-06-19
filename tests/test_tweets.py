import json


def test_get_tweets_unauthorized(client):
    """Test getting tweets without API key."""
    response = client.get('/api/tweets/')
    assert response.status_code == 401
    assert b'Api-Key required' in response.data


def test_get_tweets_success(client, auth_headers, tweet,db):
    """Test getting tweets with API key."""
    response = client.get('/api/tweets/', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['result'] is True
    assert len(data['tweets']) == 1
    assert data['tweets'][0]['content'] == 'test tweet'


def test_create_tweet_unauthorized(client):
    """Test creating tweet without API key."""
    response = client.post('/api/tweets/', json={'tweet_data': 'New tweet'})
    assert response.status_code == 401


def test_create_tweet_success(client, auth_headers, user):
    """Test creating tweet with API key."""
    response = client.post(
        '/api/tweets/',
        headers=auth_headers,
        json={'tweet_data': 'New tweet'}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['result'] is True
    assert 'tweet_id' in data


def test_create_tweet_with_media(client, auth_headers, user, attachment_factory):
    """Test creating tweet with media."""
    attachment = attachment_factory()

    response = client.post(
        '/api/tweets/',
        headers=auth_headers,
        json={
            'tweet_data': 'Tweet with media',
            'tweet_media_ids': [attachment.id]
        }
    )
    assert response.status_code == 201


def test_delete_tweet_unauthorized(client, tweet):
    """Test deleting tweet without API key."""
    response = client.delete(f'/api/tweets/{tweet.id}')
    assert response.status_code == 401


def test_delete_tweet_not_found(client, auth_headers):
    """Test deleting non-existent tweet."""
    response = client.delete('/api/tweets/999', headers=auth_headers)
    assert response.status_code == 404


def test_delete_tweet_success(client, auth_headers, tweet):
    """Test deleting tweet with API key."""
    response = client.delete(f'/api/tweets/{tweet.id}', headers=auth_headers)
    assert response.status_code == 204


def test_like_tweet_unauthorized(client, tweet):
    """Test liking tweet without API key."""
    response = client.post(f'/api/tweets/{tweet.id}/likes')
    assert response.status_code == 401


def test_like_tweet_success(client, auth_headers, tweet):
    """Test liking tweet with API key."""
    response = client.post(
        f'/api/tweets/{tweet.id}/likes',
        headers=auth_headers
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['result'] is True


def test_unlike_tweet_success(client, auth_headers, tweet, like_factory):
    """Test unliking tweet with API key."""
    response = client.post(
        f'/api/tweets/{tweet.id}/likes',
        headers=auth_headers
    )

    response = client.delete(
        f'/api/tweets/{tweet.id}/likes',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['result'] is True