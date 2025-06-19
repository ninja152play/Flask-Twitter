import json


def test_upload_media_unauthorized(client, test_file):
    """Test uploading media without API key."""
    response = client.post('/api/medias/', data={'file': test_file})
    assert response.status_code == 401

def test_upload_media_invalid_file(client, auth_headers):
    """Test uploading invalid file."""
    response = client.post(
        '/api/medias/',
        headers=auth_headers,
        data={'file': 'not-a-file'}
    )
    assert response.status_code == 400

def test_upload_media_success(client, auth_headers, test_file, app):
    """Test uploading media with valid file."""
    response = client.post(
        '/api/medias/',
        headers=auth_headers,
        data={'file': test_file}
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['result'] is True
    assert 'media_id' in data
