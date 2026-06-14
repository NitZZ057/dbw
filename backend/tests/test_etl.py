"""ETL transformation tests."""
import pandas as pd
import pytest
from etl.sources.genesis_api import GenesisPopulation
from etl.sources.rates_csv import RatesCSV
from etl.sources.unfallatlas_csv import UnfallatlasCSV
@pytest.mark.asyncio
async def test_unfallatlas_transform():
    source = UnfallatlasCSV(".")
    frame = pd.DataFrame([{"UIDENTSTLAE":"x","ULAND":"1","UREGBEZ":"0","UKREIS":"1","UGEMEINDE":"2","IstRad":1,"IstPKW":0,"IstFuss":0,"IstKrad":0,"IstGkfz":0}])
    result = await source.transform(frame)
    assert result.iloc[0]["municipality_ags"] == "01001002"
@pytest.mark.asyncio
async def test_rates_csv_transform():
    result = await RatesCSV(".").transform(pd.DataFrame([{"schluessel": "1001", "regionaleinheit":"Kiel", "wert":"12,5"}]))
    assert result.iloc[0]["schluessel"] == "01001" and result.iloc[0]["wert"] == 12.5
@pytest.mark.asyncio
async def test_genesis_transform():
    result = await GenesisPopulation(".").transform(pd.DataFrame([{"AGS":"1001", "population":100}]))
    assert result.iloc[0]["ags"] == "01001"
