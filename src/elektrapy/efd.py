import os
import glob

import networkx as nx

import pandas as pd

import plotly
import plotly.graph_objects as go
import plotly.express as px

from elektrapy import PATHWAY_NODE_MAP, CYCLE_COLOR_MAP
from elektrapy.indices import get_redox_index, get_aggregated_potential


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
    redox_df = get_aggregated_potential(
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
    label_var: str,
    color_var: str = "count",
    cycle_color_map: dict = CYCLE_COLOR_MAP
) -> go.Figure:

    # Add cycle color to nodes
    node_df["node_color"] = node_df["node"].map(
        _get_node_colors(cycle_color_map)
    )

    # Scale nodes to fit in the Sankey diagram
    node_df = _scale_nodes(node_df)

    fig = go.Figure(
        go.Sankey(
            domain={
                "x": [0.0, 1.0],
                "y": [0.0, 1.0]
            },
            orientation="h",
            arrangement="freeform",
            # valuesuffix="genomes",
            node={
                # NOTE: use categories here and in the link definition to avoid
                # errors when creating the Sankey (interally sorts the nodes)
                "label": node_df["node"].cat.categories,
                # "x": [0.25, 0.45, 0.65, 0.85, 0.05],
                # "y": [0.05, 0.30, 0.50, 0.75, 0.55],
                "color": node_df["node_color"].values.tolist(),
                "thickness": 20,
                "pad": 10
            },
            link={
                # HMM hits define enzymes present and, thus, substrates and products
                "source": network_df["source"].cat.codes.tolist(),
                "target": network_df["target"].cat.codes.tolist(),

                # Define number of links by gene copy number and/or abundance
                "value": network_df["count_perc"].values.tolist(),

                # Color by chosen variable (sample, dataset, temperature, pH, etc.)
                "color": network_df[f"link_color_{color_var}"].values.tolist(),
                "label": network_df[label_var].values.tolist(),

                "arrowlen": 15
            }
        )
    )

    # # Create legends
    # legend_dataset = [
    #     go.Scatter(
    #         mode="lines",
    #         x=[None],
    #         y=[None],
    #         marker=dict(size=10, color=color, symbol="square"),
    #         name=key,
    #         legendgroup="color_var",
    #         legendgrouptitle={
    #             "text": f"{color_var.capitalize()} (links)"
    #         }
    #     )
    #     for key, color in network_df[
    #         [color_var, f"link_color_{color_var}"]
    #     ].drop_duplicates().values
    # ]
    # for trace in legend_dataset:
    #     fig.add_trace(trace)

    fig.update_layout(
        title=f"Sankey diagram colored by {color_var}",
        width=1000,
        height=750,
        font=dict(
            size=11,
            family="Arial"
        ),
        legend=dict(
            yanchor="top",
            # y=0.99,
            xanchor="right",
            # x=0.01
        ),
        paper_bgcolor="#f8f7f2",
        plot_bgcolor="#f8f7f2"
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # Fix aspect ratio
    # See: https://github.com/plotly/plotly.js/issues/4847#issuecomment-1500911948
    fig.update_traces(
        domain_y=list([0, 0.75]),
        selector=dict(type="sankey")
    )

    return fig


def _get_node_colors(cycle_color_map: dict) -> pd.DataFrame:

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
