"""Accident endpoint tests."""
import pytest
@pytest.mark.asyncio
async def test_count_all_accidents(client):
    assert (await client.get("/accidents/count")).json()["data"]["count"] == 10
@pytest.mark.asyncio
async def test_filter_by_state_ags(client):
    assert (await client.get("/accidents/count?state_ags=14")).json()["data"]["count"] == 10
@pytest.mark.asyncio
async def test_filter_by_pedestrian(client):
    assert (await client.get("/accidents/count?ist_fuss=true")).json()["data"]["count"] == 2
@pytest.mark.asyncio
async def test_filter_by_year(client):
    assert (await client.get("/accidents/count?year=2021")).json()["data"]["count"] == 3
@pytest.mark.asyncio
async def test_earliest_year(client):
    assert (await client.get("/time/earliest")).json()["data"]["earliest_year"] == 2021
@pytest.mark.asyncio
async def test_invalid_page_size(client):
    assert (await client.get("/accidents?page_size=999")).status_code == 422
