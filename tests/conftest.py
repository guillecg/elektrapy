import pytest

import os

import pandas as pd

from elektrapy.efd import get_node_df


@pytest.fixture(scope="session", autouse=True)
def color_var() -> str:
    yield "type"


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
def network_df_group(
    network_df_sample: pd.DataFrame,
    metadata_df: pd.DataFrame,
    color_var: str
) -> pd.DataFrame:
    network_df_group = pd.merge(
        left=network_df_sample,
        right=metadata_df[["sample_id", color_var]].drop_duplicates(),
        how="inner",
        on="sample_id"
    )

    network_df_group = network_df_group\
        .groupby([color_var, "source", "target"], as_index=False)["value"]\
        .sum()

    yield network_df_group


@pytest.fixture(scope="session", autouse=True)
def redox_df() -> pd.DataFrame:
    redox_df = pd.read_csv("data/redox-potentials.csv")

    # Skip first row containing the units
    redox_df = redox_df.iloc[1:]

    yield redox_df


@pytest.fixture(scope="session", autouse=True)
def node_df_sample(
    network_df_sample: pd.DataFrame,
    redox_df: pd.DataFrame,
    group_var: str = "sample_id"
) -> pd.DataFrame:
    yield get_node_df(
        network_df=network_df_sample,
        redox_df=redox_df,
        group_var=group_var
    )


@pytest.fixture(scope="session", autouse=True)
def link_color_map() -> dict:
    yield {
        "surface": "#FFC349",
        "aquifer": "#97DDE9",
        "mine": "#525EA7",
        "reservoir": "#EB7F31"
    }
