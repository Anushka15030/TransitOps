def test_driver_create_creates_user_atomically(client, db_session, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}

    res = client.post("/api/v1/drivers", json={
        "full_name": "Test Driver", "email": "testdriver@example.com", "phone": "+911111111111",
        "password": "Passw0rd123", "license_number": "DL1111111111111", "license_expiry": "2030-01-01",
    }, headers=headers)
    assert res.status_code == 201
    driver_id = res.json()["id"]
    assert res.json()["email"] == "testdriver@example.com"

    # The created account can log in
    login_res = client.post("/api/v1/auth/login", json={
        "email": "testdriver@example.com", "password": "Passw0rd123",
    })
    assert login_res.status_code == 200
    assert login_res.json()["user"]["role"] == "driver"

    return driver_id


def test_driver_duplicate_license_rejected(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "full_name": "First Driver", "email": "first@example.com", "phone": "+912222222222",
        "password": "Passw0rd123", "license_number": "DL2222222222222", "license_expiry": "2030-01-01",
    }
    res1 = client.post("/api/v1/drivers", json=payload, headers=headers)
    assert res1.status_code == 201

    payload["email"] = "second@example.com"
    payload["phone"] = "+913333333333"
    res2 = client.post("/api/v1/drivers", json=payload, headers=headers)  # same license_number
    assert res2.status_code == 409


def test_driver_delete_preserves_user_account(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post("/api/v1/drivers", json={
        "full_name": "Delete Me", "email": "deleteme@example.com", "phone": "+914444444444",
        "password": "Passw0rd123", "license_number": "DL4444444444444", "license_expiry": "2030-01-01",
    }, headers=headers)
    driver_id = res.json()["id"]

    del_res = client.delete(f"/api/v1/drivers/{driver_id}", headers=headers)
    assert del_res.status_code == 204

    login_res = client.post("/api/v1/auth/login", json={
        "email": "deleteme@example.com", "password": "Passw0rd123",
    })
    assert login_res.status_code == 200  # user account still exists and can log in