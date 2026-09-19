import pytest

import os

import pandas as pd

from elektrapy.indices import get_redox_index, get_mean_potential


@pytest.fixture(scope="module", autouse=False)
def network_df_genome(data_dir: str) -> pd.DataFrame:
    yield pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            "network-genome.csv"
        )
    )


@pytest.fixture(scope="module", autouse=False)
def network_df_sample(data_dir: str) -> pd.DataFrame:
    yield pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            "network-sample.csv"
        )
    )


def test_get_redox_index_genome(
    data_dir: str,
    network_df_genome: pd.DataFrame,
    group_var: str = "genome_id"
) -> None:
    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"indices-rti-{group_var.split('_')[0]}.csv"
            )
        ),
        right=get_redox_index(
            network_df=network_df_genome,
            group_var=group_var
        ).reset_index(drop=True)
    )


def test_get_redox_index_sample(
    data_dir: str,
    network_df_sample: pd.DataFrame,
    group_var: str = "sample_id"
) -> None:
    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"indices-rti-{group_var.split('_')[0]}.csv"
            )
        ),
        right=get_redox_index(
            network_df=network_df_sample,
            group_var=group_var
        ).reset_index(drop=True)
    )
