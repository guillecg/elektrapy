import pytest

import os

import pandas as pd

from elektrapy.efd import get_node_df


def test_get_node_df_genome(
    data_dir: str,
    network_df_genome: pd.DataFrame,
    redox_df: pd.DataFrame,
    group_var: str = "genome_id"
) -> None:
    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"nodes-{group_var.split('_')[0]}.csv"
            )
        ),
        right=get_node_df(
            network_df=network_df_genome,
            redox_df=redox_df,
            group_var=group_var
        )
    )


def test_get_node_df_sample(
    data_dir: str,
    network_df_sample: pd.DataFrame,
    redox_df: pd.DataFrame,
    group_var: str = "sample_id"
) -> None:
    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"nodes-{group_var.split('_')[0]}.csv"
            )
        ),
        right=get_node_df(
            network_df=network_df_sample,
            redox_df=redox_df,
            group_var=group_var
        )
    )
