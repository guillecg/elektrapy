import pytest

import os

import pandas as pd


@pytest.fixture(scope="session", autouse=True)
def data_dir() -> str:
    yield "tests/data/"


@pytest.fixture(scope="session", autouse=True)
def metadata_df(data_dir) -> pd.DataFrame:
    yield pd.read_csv(
        os.path.join(
            data_dir,
            "metadata.csv"
        )
    )


@pytest.fixture(scope="session", autouse=True)
def pathway_df(data_dir) -> pd.DataFrame:
    yield pd.read_table(
        os.path.join(
            data_dir,
            "bigecyhmm",
            "pathway_presence.tsv"
        )
    )


@pytest.fixture(scope="session", autouse=True)
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


@pytest.fixture(scope="session", autouse=True)
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


@pytest.fixture(scope="session", autouse=True)
def redox_df() -> pd.DataFrame:
    redox_df = pd.read_csv("data/redox-potentials.csv")

    # Skip first row containing the units
    redox_df = redox_df.iloc[1:]

    yield redox_df
