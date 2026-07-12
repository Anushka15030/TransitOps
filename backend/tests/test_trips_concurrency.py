# tests/test_trips_concurrency.py
"""
Simulates two dispatchers racing to dispatch overlapping trips for the
SAME driver. Without row locking, both could pass the overlap check
(read before either writes) and both succeed — a real double-booking.
With locking, exactly one must win.
"""
import threading

def test_concurrent_dispatch_only_one_succeeds(client, admin_token, draft_trip_a, draft_trip_b_same_driver):
    headers = {"Authorization": f"Bearer {admin_token}"}
    results = []

    def dispatch(trip_id):
        res = client.post(f"/api/v1/trips/{trip_id}/dispatch", headers=headers)
        results.append(res.status_code)

    t1 = threading.Thread(target=dispatch, args=(draft_trip_a,))
    t2 = threading.Thread(target=dispatch, args=(draft_trip_b_same_driver,))
    t1.start(); t2.start()
    t1.join(); t2.join()

    # Exactly one 200, exactly one 409 — never two 200s.
    assert sorted(results) == [200, 409]