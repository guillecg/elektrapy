import pytest

import os

import pandas as pd

from elektrapy import PATHWAY_NODE_MAP, NODE_CYCLE_MAP, CYCLE_COLOR_MAP
from elektrapy.efd import (
    get_node_df,
    get_efd,
    get_rti_plot,
    _get_node_colors,
    _scale_nodes,
    _encode_nodes,
    _highlight_node
)


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


def test__get_node_colors_sample(
    data_dir: str,
    node_df_sample: pd.DataFrame,
    color_var: str,
    cycle_color_map: dict = CYCLE_COLOR_MAP
) -> None:

    node_df = node_df_sample.copy()

    # Add cycle color to nodes
    node_df["node_color"] = node_df["node"].map(
        _get_node_colors(cycle_color_map)
    )

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"nodes-color-{color_var}.csv"
            )
        ),
        right=node_df
    )


def test__scale_nodes(
    data_dir: str,
    node_df_sample: pd.DataFrame,
    color_var: str,
    cycle_color_map: dict = CYCLE_COLOR_MAP
) -> None:

    node_df = node_df_sample.copy()

    # Add cycle color to nodes
    node_df["node_color"] = node_df["node"].map(
        _get_node_colors(cycle_color_map)
    )

    # Scale nodes to fit in the Sankey diagram
    node_df = _scale_nodes(node_df)

    # Fix dtypes for comparison
    node_df["node"] = node_df["node"].astype(str)
    node_df["redox_index"] = node_df["redox_index"].astype(float)
    node_df["transformed_potential"] = node_df["transformed_potential"]\
        .astype(float)

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"nodes-scale-{color_var}.csv"
            )
        ),
        right=node_df
    )
