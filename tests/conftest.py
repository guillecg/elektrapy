import pytest

import os

import pandas as pd


@pytest.fixture(scope="session", autouse=True)
def data_dir() -> str:
    yield "tests/data/"


@pytest.fixture(scope="session", autouse=True)
def network_df_genome(data_dir: str) -> pd.DataFrame:
    yield pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            "network-genome.csv"
        )
    )


@pytest.fixture(scope="session", autouse=True)
def network_df_sample(data_dir: str) -> pd.DataFrame:
    yield pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            "network-sample.csv"
        )
    )
