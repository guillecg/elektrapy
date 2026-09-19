import pytest

import os

import pandas as pd

from elektrapy.preprocessing import preprocess_data


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
    metadata_df: pd.DataFrame
) -> None:
    pd.testing.assert_frame_equal(
        left=results_df_sample,
        right=preprocess_data(
            df=pathway_df,
            group_var="sample_id",
            mapping=dict(
                zip(
                    metadata_df["genome_id"],
                    metadata_df["sample_id"]
                )
            )
        )
    )
