import pytest

import os

import pandas as pd
from pandas.api.types import CategoricalDtype

import plotly.graph_objects as go

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


def test_get_efd(
    data_dir: str,
    node_df_sample: pd.DataFrame,
    network_df_group: pd.DataFrame,
    color_var: str,
    link_color_map: dict,
    cycle_color_map: dict = CYCLE_COLOR_MAP,
    highlight_node: str = "H2",
    link_alpha: float = 0.1
) -> None:
    fig = get_efd(
        network_df=network_df_group,
        node_df=node_df_sample,
        color_var=color_var,
        link_color_map=link_color_map,
        cycle_color_map=cycle_color_map,
        highlight_node="H2",
        link_alpha=0.1
    )
    assert isinstance(fig, go.Figure)


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


def test__encode_nodes(
    data_dir: str,
    node_df_sample: pd.DataFrame,
    network_df_group: pd.DataFrame,
    color_var: str,
    cycle_color_map: dict = CYCLE_COLOR_MAP
) -> None:

    node_df = node_df_sample.copy()
    network_df = network_df_group.copy()

    # Add cycle color to nodes
    node_df["node_color"] = node_df["node"].map(
        _get_node_colors(cycle_color_map)
    )

    # Scale nodes to fit in the Sankey diagram
    node_df = _scale_nodes(node_df)

    # Encode nodes as categories
    node_df, network_df = _encode_nodes(
        node_df=node_df,
        network_df=network_df
    )

    # Fix dtypes for comparison
    node_df["redox_index"] = node_df["redox_index"].astype(float)
    node_df["transformed_potential"] = node_df["transformed_potential"]\
        .astype(float)

    # Manually encode categories
    node_df_test = pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            f"nodes-coded-{color_var}.csv"
        )
    )
    categories = CategoricalDtype(
        categories=node_df["node"].unique(),
        ordered=True
    )
    node_df_test["node"] = node_df_test["node"].astype(categories)

    pd.testing.assert_frame_equal(
        left=node_df_test,
        right=node_df
    )


def test__highlight_node(
    data_dir: str,
    node_df_sample: pd.DataFrame,
    network_df_group: pd.DataFrame,
    color_var: str,
    link_color_map: dict,
    cycle_color_map: dict = CYCLE_COLOR_MAP,
    highlight_node: str = "H2",
    link_alpha: float = 0.1
) -> None:

    node_df = node_df_sample.copy()
    network_df = network_df_group.copy()

    # Add cycle color to nodes
    node_df["node_color"] = node_df["node"].map(
        _get_node_colors(cycle_color_map)
    )

    # Scale nodes to fit in the Sankey diagram
    node_df = _scale_nodes(node_df)

    # Encode nodes as categories
    node_df, network_df = _encode_nodes(
        node_df=node_df,
        network_df=network_df
    )

    # ------------------------------------------------------------------------ #
    # Links

    link_var = f"link_color_{color_var}"

    network_df[link_var] = network_df[color_var].map(link_color_map)

    network_df = _highlight_node(
        network_df=network_df,
        color_var=link_var,
        alpha=link_alpha,
        node=highlight_node
    )

    # Manually encode categories
    network_df_test = pd.read_csv(
        os.path.join(
            data_dir,
            "results",
            f"network-highlight-{color_var}.csv"
        )
    )
    node_df, network_df_test = _encode_nodes(
        node_df=node_df,
        network_df=network_df_test
    )

    # Sort to match order in test dataframe
    network_df = network_df.sort_values("target")

    pd.testing.assert_frame_equal(
        left=network_df_test.reset_index(drop=True),
        right=network_df.reset_index(drop=True),
        check_like=True
    )
