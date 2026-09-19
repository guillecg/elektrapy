import pytest

import os

import pandas as pd

from elektrapy.preprocessing import *


@pytest.fixture(scope="module", autouse=True)
def metadata_df(data_dir) -> pd.DataFrame:
    yield pd.read_csv(
        os.path.join(
            data_dir,
            "metadata.csv"
        )
    )


@pytest.fixture(scope="module", autouse=True)
def pathway_df(data_dir) -> pd.DataFrame:
    yield pd.read_table(
        os.path.join(
            data_dir,
            "bigecyhmm",
            "pathway_presence.tsv"
        )
    )


@pytest.fixture(scope="module", autouse=True)
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


@pytest.fixture(scope="module", autouse=True)
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


@pytest.fixture(scope="module", autouse=True)
def network_df_genome(data_dir: str) -> pd.DataFrame:
    yield pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            "network-genome.csv"
        )
    )


@pytest.fixture(scope="module", autouse=True)
def network_df_sample(data_dir: str) -> pd.DataFrame:
    yield pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            "network-sample.csv"
        )
    )


@pytest.fixture(scope="module", autouse=False)
def mapping(metadata_df: pd.DataFrame) -> dict:
    yield dict(
        zip(
            metadata_df["genome_id"],
            metadata_df["sample_id"]
        )
    )


def test_preprocess_data_genome(
    pathway_df: pd.DataFrame,
    results_df_genome: pd.DataFrame
) -> None:
    pd.testing.assert_frame_equal(
        left=results_df_genome,
        right=preprocess_data(
            df=pathway_df,
            group_var="genome_id"
        )
    )


def test_preprocess_data_sample(
    pathway_df: pd.DataFrame,
    results_df_sample: pd.DataFrame,
    metadata_df: pd.DataFrame,
    mapping: dict
) -> None:
    pd.testing.assert_frame_equal(
        left=results_df_sample,
        right=preprocess_data(
            df=pathway_df,
            group_var="sample_id",
            mapping=mapping
        )
    )


@pytest.mark.parametrize(("group_var", "mapping"), [
    ("genome_id", None),
    ("sample_id", mapping),
    pytest.param(
        "other",
        None,
        marks=pytest.mark.xfail(reason="Not implemented.")
    ),
    pytest.param(
        "other",
        mapping,
        marks=pytest.mark.xfail(reason="Not implemented.")
    )
], indirect=["mapping"])
def test_preprocess_data_group_var(
    pathway_df: pd.DataFrame,
    group_var: str,
    mapping: dict
) -> None:
    preprocess_data(
        df=pathway_df,
        group_var=group_var,
        mapping=mapping
    )


@pytest.mark.parametrize(("group_var", "fn_var", "mapping"), [
    ("genome_id", "function", None),
    ("sample_id", "function", mapping),
    pytest.param(
        "genome_id",
        "other",
        None,
        marks=pytest.mark.xfail(reason="Column not originally found in data.")
    ),
    pytest.param(
        "sample_id",
        "other",
        mapping,
        marks=pytest.mark.xfail(reason="Column not originally found in data.")
    )
], indirect=["mapping"])
def test_preprocess_data_fn_var(
    pathway_df: pd.DataFrame,
    group_var: str,
    fn_var: str,
    mapping: dict
) -> None:
    results_df_genome = preprocess_data(
        df=pathway_df,
        group_var=group_var,
        fn_var=fn_var,
        mapping=mapping
    )


def test_get_network_df_genome(
    results_df_genome: pd.DataFrame,
    network_df_genome: pd.DataFrame
) -> None:

    network_df = get_network_df(
        results_df=results_df_genome,
        group_var="genome_id"
    )
    network_df = network_df.reset_index(drop=True)

    pd.testing.assert_frame_equal(
        left=network_df_genome,
        right=network_df
    )


def test_get_network_df_sample(
    results_df_sample: pd.DataFrame,
    network_df_sample: pd.DataFrame
) -> None:
    pd.testing.assert_frame_equal(
        left=network_df_sample,
        right=get_network_df(
            results_df=results_df_sample,
            group_var="sample_id"
        )
    )
