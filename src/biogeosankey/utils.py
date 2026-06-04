import os
import glob

import networkx as nx

import pandas as pd

import plotly
import plotly.graph_objects as go
import plotly.express as px

from biogeosankey import PATHWAY_NODES_MAP


def load_bigecyhmm_results(bigec_dir: str) -> pd.DataFrame:

    bigec_pattern = ".R_input.txt"
    glob_pattern = os.path.join(
        bigec_dir,
        f"diagram_input/*{bigec_pattern}"
    )

    bigec_df = []

    for filename in glob.glob(glob_pattern):
        genome_id = os.path.basename(filename).replace(bigec_pattern, "")
        genome_df = pd.read_table(
            filename,
            names=["pathway", "count"]
        )
        genome_df["genome_id"] = genome_id
        bigec_df.append(genome_df)

    return pd.concat(bigec_df)


def process_bigecyhmm(path: str) -> pd.DataFrame:

    network_df = load_bigecyhmm_results(path)

    # Add cycle
    network_df["cycle"] = network_df["pathway"]\
        .str.split("-")\
        .str[0]\
        .map({
            "C": "carbon",
            "N": "nitrogen",
            "O": "other",
            "S": "sulfur"
        })

    # Add sources and targets (i.e. substrates and products)
    network_df[["source", "target"]] = network_df["pathway"]\
        .replace(PATHWAY_NODES_MAP)\
        .str.split(" -> ", expand=True)

    # Drop pathways without sources or targets (i.e. not mapped)
    network_df = network_df.dropna(subset="source")
    network_df = network_df.dropna(subset="target")

    # Explode multiple sources (e.g. methanogenesis)
    network_df["source"] = network_df["source"].str.split(";")
    network_df = network_df.explode("source")

    # Explode multiple targets (e.g. from disproportionation)
    network_df["target"] = network_df["target"].str.split(";")
    network_df = network_df.explode("target")

    return network_df


def get_colors(
    points: list,
    colorscale: str = "Sunset_r"
) -> list:
    return plotly.colors.sample_colorscale(
        colorscale=colorscale,
        samplepoints=points,
        low=0.0,
        high=1.0,
        colortype="rgb"
    )


def get_node_data(network_df: pd.DataFrame) -> pd.DataFrame:
    # Calculate degree percentage per node

    # NOTE: multiple species can participate in more than one reaction. For
    # example, SO3 can be oxidized or reduced, so to sum percentages we need to 
    # keep track of n_genomes twice (one for oxidation, one for reduction)

    target_df = network_df\
        .groupby(["cycle", "target"], as_index=False)\
        [["count", "n_genomes"]]\
        .sum()
    target_df["degree_in_ratio"] = \
        target_df["count"] / target_df["n_genomes"]
    target_df = target_df\
        .rename(columns={"target": "node"})\
        .drop(["count", "n_genomes"], axis=1)

    source_df = network_df\
        .groupby(["cycle", "source"], as_index=False)\
        [["count", "n_genomes"]]\
        .sum()
    source_df["degree_out_ratio"] = \
        source_df["count"] / source_df["n_genomes"]
    source_df = source_df\
        .rename(columns={"source": "node"})\
        .drop(["count", "n_genomes"], axis=1)

    node_df = pd.merge(
        left=target_df,
        right=source_df,
        on=["cycle", "node"],
        how="outer" # Outer to allow source-only or target-only nodes
    )

    # Calculate percentage change (positive if acceptor, negative if donor)
    node_df["redox_index"] = \
        (node_df["degree_in_ratio"] - node_df["degree_out_ratio"]) / \
        node_df["degree_out_ratio"]

    # Fill missing targets/sources in source-only and target-only nodes
    node_df = node_df.fillna(0.0)

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
