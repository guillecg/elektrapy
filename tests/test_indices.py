import os

import pandas as pd

from elektrapy.indices import get_redox_index, get_mean_potential


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
        ).sort_values("node").reset_index(drop=True),
        right=get_redox_index(
            network_df=network_df_genome,
            group_var=group_var
        ).sort_values("node").reset_index(drop=True)
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
        ).sort_values("node").reset_index(drop=True),
        right=get_redox_index(
            network_df=network_df_sample,
            group_var=group_var
        ).sort_values("node").reset_index(drop=True)
    )


def test_get_mean_potential_genome(
    data_dir: str,
    network_df_genome: pd.DataFrame,
    redox_df: pd.DataFrame,
    group_var: str = "genome_id"
) -> None:

    rti_df = get_redox_index(
        network_df=network_df_genome,
        group_var=group_var
    )

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"indices-redox-{group_var.split('_')[0]}.csv"
            )
        ).sort_values("node").reset_index(drop=True),
        right=get_mean_potential(
            redox_df=redox_df,
            rti_df=rti_df
        ).sort_values("node").reset_index(drop=True)
    )


def test_get_mean_potential_sample(
    data_dir: str,
    network_df_sample: pd.DataFrame,
    redox_df: pd.DataFrame,
    group_var: str = "sample_id"
) -> None:

    rti_df = get_redox_index(
        network_df=network_df_sample,
        group_var=group_var
    )

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"indices-redox-{group_var.split('_')[0]}.csv"
            )
        ).sort_values("node").reset_index(drop=True),
        right=get_mean_potential(
            redox_df=redox_df,
            rti_df=rti_df
        ).sort_values("node").reset_index(drop=True)
    )
