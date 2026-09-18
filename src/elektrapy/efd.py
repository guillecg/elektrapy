import os
import glob

import networkx as nx

import pandas as pd

import plotly
import plotly.graph_objects as go
import plotly.express as px

from elektrapy import PATHWAY_NODE_MAP, CYCLE_COLOR_MAP


def get_node_df(
    network_df: pd.DataFrame,
    redox_df: pd.DataFrame
) -> pd.DataFrame:

    # X axis: the Redox Tendency Index
    rti_df = get_redox_index(
        network_df=network_df_sample,
        group_var="sample_id"
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


def create_sankey(
    network_df: pd.DataFrame,
    node_df: pd.DataFrame,
    label_var: str,
    color_var: str = "count"
) -> go.Figure:
    # See: https://stackoverflow.com/questions/74657646/plotly-sankey-how-to-use-defined-node-positions-with-vertical-orientation-wit

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
