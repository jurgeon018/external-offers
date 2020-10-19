async def test_ping(http):
    await http.request('GET', '/ping/', expected_status=200)
