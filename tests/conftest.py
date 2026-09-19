import pytest

import os

import pandas as pd


@pytest.fixture(scope="session", autouse=True)
def data_dir() -> str:
    yield "tests/data/"


@pytest.fixture(scope="module", autouse=False)
def results_df_genome(data_dir: str) -> pd.DataFrame:
    results_df = pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            "results-genome.csv"
        )
    )

    # Add name to column list
    results_df.columns.name = "pathway"

    yield results_df


@pytest.fixture(scope="module", autouse=False)
def results_df_sample(data_dir: str) -> pd.DataFrame:
    results_df = pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            "results-sample.csv"
        )
    )

    # Add name to column list
    results_df.columns.name = "pathway"

    yield results_df


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
