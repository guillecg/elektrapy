from typing import List

import os
import glob

import networkx as nx

import pandas as pd
from pandas.api.types import CategoricalDtype

import plotly
import plotly.graph_objects as go
import plotly.express as px
from plotly.colors import hex_to_rgb

from sklearn.preprocessing import minmax_scale

from elektrapy import PATHWAY_NODE_MAP, NODE_CYCLE_MAP, CYCLE_COLOR_MAP
from elektrapy.indices import get_redox_index, get_mean_potential


def get_node_df(
    network_df: pd.DataFrame,
    redox_df: pd.DataFrame,
    group_var: str = "sample_id"
) -> pd.DataFrame:

    # X axis: the Redox Tendency Index
    rti_df = get_redox_index(
        network_df=network_df,
        group_var=group_var
    )

    # Y axis: the mean of the transformed Eº'
    redox_df = get_mean_potential(
        redox_df=redox_df,
        rti_df=rti_df
    )

    node_df = pd.merge(
        left=rti_df,
        right=redox_df,
        on="node",
        how="inner"
    )

    return node_df


def get_efd(
    network_df: pd.DataFrame,
    node_df: pd.DataFrame,
    color_var: str,
    link_color_map: dict,
    cycle_color_map: dict = CYCLE_COLOR_MAP,
    highlight_node: str = "H2",
    link_alpha: float = 0.1
) -> go.Figure:

    # ------------------------------------------------------------------------ #
    # Nodes

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

    # ------------------------------------------------------------------------ #

    fig = go.Figure(
        go.Sankey(
            domain={
                "x": [0.0, 1.0],
                "y": [0.0, 1.0]
            },
            orientation="h",
            arrangement="freeform",

            node={
                # NOTE: use categories here and in the link definition to avoid
                # errors when creating the Sankey (interally sorts the nodes)
                "label": node_df["node"].cat.categories,

                "x": node_df["redox_index_minmax"].values.tolist(),
                "y": node_df["transformed_potential_minmax"].values.tolist(),
                "color": node_df["node_color"].values.tolist(),

                "thickness": 10,
                "pad": 20
            },
            link={
                "label": network_df[color_var].values.tolist(),

                "source": network_df["source"].cat.codes.tolist(),
                "target": network_df["target"].cat.codes.tolist(),
                "color": network_df[link_var].values.tolist(),

                # Define number of links by gene copy number and/or abundance
                "value": network_df["value"].values.tolist(),

                "arrowlen": 15
            }
        )
    )

    # Create legends
    legend_dataset = [
        go.Scatter(
            mode="lines",
            x=[None],
            y=[None],
            marker=dict(size=10, color=color, symbol="square"),
            name=key,
            legendgroup="color_var",
            legendgrouptitle={
                "text": f"{color_var.capitalize()} (links)"
            }
        )
        for key, color in link_color_map.items()
    ]
    legend_dataset.extend([
        go.Scatter(
            mode="markers",
            x=[None],
            y=[None],
            marker=dict(size=10, color=color, symbol="square"),
            name=key,
            legendgroup="cycle",
            legendgrouptitle={
                "text": "Cycle (nodes)"
            }
        )
        for key, color in cycle_color_map.items()
    ])

    for trace in legend_dataset:
        fig.add_trace(trace)

    fig.update_layout(
        width=1000,
        height=750,
        font=dict(
            size=15,
            # weight="bold",
            family="Arial"
        ),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    # Change to true to plot the axes
    fig.update_xaxes(
        title="Redox Tendency Index (RTI)",
        visible=True,
        tickvals=[1, 0, -1],
        range=[-1, 1]
    )
    fig.update_yaxes(
        title="Mean Eº'",
        visible=True,
        tickvals=[-1, -0.5, 0, 0.5, 1, 1.3],
        range=[1.3, -1.5]
    )

    return fig


def _get_node_colors(
    cycle_color_map: dict,
    node_cycle_map: dict = NODE_CYCLE_MAP,
) -> pd.DataFrame:

    node_colors = pd.DataFrame\
        .from_dict(node_cycle_map, orient="index")\
        .reset_index()\
        .rename(columns={"index": "node", 0: "cycle"})

    node_colors["color"] = node_colors["cycle"].map(cycle_color_map)
    node_colors = dict(zip(node_colors["node"], node_colors["color"]))

    return node_colors


def _scale_nodes(node_df: pd.dataframe) -> pd.DataFrame:

    # Manually add minimum and maximum to force the range before scaling
    node_df = pd.concat([
        node_df,
        pd.Series({
            "node": "minimum",
            "redox_index": -1,
            "transformed_potential": -1.5
        }).to_frame().T,
        pd.Series({
            "node": "maximum",
            "redox_index": 1,
            "transformed_potential": 1
        }).to_frame().T
    ])

    # Transform axes to fit within the range of [0, 1] for the Sankey diagram
    node_df["redox_index_minmax"] = minmax_scale(
        node_df["redox_index"]
    )
    node_df["transformed_potential_minmax"] = minmax_scale(
        node_df["transformed_potential"]
    )

    # Drop artificial nodes
    node_df = node_df[~node_df["node"].isin(["minimum", "maximum"])].copy()

    return node_df


def _encode_nodes(
    node_df: pd.DataFrame,
    network_df: pd.DataFrame
) -> List[pd.DataFrame, pd.DataFrame]:

    categories = CategoricalDtype(
        categories=node_df["node"].unique(),
        ordered=True
    )

    # Encode as categories for plotting
    node_df["node"] = node_df["node"].astype(categories)
    network_df["source"] = network_df["source"].astype(categories)
    network_df["target"] = network_df["target"].astype(categories)

    # Force sorting according to categories for maintaining order in Sankey
    # NOTE: missing categories may alter order of colors!
    node_df = node_df.sort_values("node")
    network_df = network_df.sort_values("target")

    return [node_df, network_df]


def _highlight_node(
    network_df: pd.DataFrame,
    color_var: str,
    alpha: float = 0.1,
    node: str = "H2"
) -> pd.DataFrame:

    # Modify link opacity
    network_df[color_var] = network_df[color_var]\
        .apply(lambda row: f"rgb{hex_to_rgb(row)}")\
        .apply(lambda row: row.replace("rgb", "rgba"))\
        .apply(lambda row: row.replace(")", f", {alpha})"))

    network_df.loc[
        (network_df["source"] == node),
        color_var
    ] = network_df.loc[
        (network_df["source"] == node),
        color_var
    ].str.replace(f", {alpha})", ", 1)")

    return network_df
