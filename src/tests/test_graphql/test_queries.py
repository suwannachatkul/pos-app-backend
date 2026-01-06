def test_graphql_queries(client):
    query = """
    query {
      hello
      health
    }
    """
    resp = client.post("/graphql", json={"query": query})
    assert resp.status_code == 200
    data = resp.json().get("data")
    assert data["hello"].startswith("Hello")
    assert "running" in data["health"]
