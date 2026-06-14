"""Aggregate endpoint tests."""
import pytest
@pytest.mark.asyncio
async def test_aggregate_by_state(client):
    response = await client.get("/aggregates/accidents?level=state")
    assert response.status_code == 200
    assert response.json()["data"][0]["accident_count"] == 10
@pytest.mark.asyncio
async def test_rate_requires_population(client):
    response = await client.get("/aggregates/rates?year=2023&level=district")
    assert response.status_code == 200
    assert [row["ags"] for row in response.json()["data"]] == ["14521"]
