def test_file_upload(client, db_session):
    token = "Bearer YOUR_TEST_TOKEN_HERE"
    files = {"file": ("test.txt", b"Hello world")}
    response = client.post("/tutor/upload", files=files, headers={"Authorization": token})
    assert response.status_code == 200
    data = response.json()
    assert "file_name" in data
