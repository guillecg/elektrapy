import pandas as pd

from elektrapy import PATHWAY_NODES_MAP


def get_aggregated_potential() -> pd.Series:
    pass


def get_redox_index(
    results_df: pd.DataFrame,
    group_var: str
) -> pd.DataFrame:

    network_df = results_df\
        .reset_index()\
        .melt(id_vars=group_var)\
        .sort_values(group_var)

    # Drop pathways without presence
    network_df = network_df[network_df["value"] == 1]

    # Extract nodes from "pathway" column
    network_df = _get_nodes(network_df)

    n_records = network_df["genome_id"].nunique()

    # Get number of times of source/target per genome
    transform_dict = dict(value="sum")

    source_df = network_df\
        .groupby(["genome_id", "source"], as_index=False, observed=True)\
        .agg(transform_dict)

    target_df = network_df\
        .groupby(["genome_id", "target"], as_index=False, observed=True)\
        .agg(transform_dict)

    # Some nodes can appear more than once if they are in different pathways
    # NOTE: cap the maximum to 1, to avoid counts higher than n_records
    source_df.loc[
        source_df["value"] > 1,
        "value"
    ] = 1
    target_df.loc[
        source_df["value"] > 1,
        "value"
    ] = 1

    # Calculate percentage of outbound connections over total for sources
    # NOTE: negative indicates tendency to be donor
    source_df = source_df\
        .rename(columns={"source": "node"})\
        .value_counts("node")\
        .reset_index()

    source_df["count"] = -source_df["count"] / n_records

    # Calculate percentage of incoming connections over total for targets
    # NOTE: positive indicates tendency to be acceptor
    target_df = target_df\
        .rename(columns={"target": "node"})\
        .value_counts("node")\
        .reset_index()

    target_df["count"] = target_df["count"] / n_records

    # Calculate the Redox Tendency Index as the sum of both
    rti_df = pd.concat([source_df, target_df])\
        .rename(columns={"count": "redox_index"})\
        .groupby("node", as_index=False)\
        .sum()\
        .sort_values("redox_index")

    return rti_df


def _get_nodes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auxiliary function for parsing the results and getting both the source 
    and target nodes as well as their corresponding biogeochemical cycle.
    """

    assert len(df), "[ERROR] Empty dataframe."

    # Add cycle
    df["cycle"] = df["pathway"]\
        .str.split("-")\
        .str[0]\
        .map({
            "C": "carbon",
            "N": "nitrogen",
            "O": "other",
            "S": "sulfur"
        })

    # Add sources and targets (i.e. substrates and products)
    df[["source", "target"]] = df["pathway"]\
        .replace(PATHWAY_NODES_MAP)\
        .str.split(" -> ", expand=True)

    # Drop pathways without sources or targets (i.e. not mapped)
    df = df.dropna(subset="source")
    df = df.dropna(subset="target")

    # Explode multiple sources (e.g. methanogenesis)
    df["source"] = df["source"].str.split(";")
    df = df.explode("source")

    # Explode multiple targets (e.g. from disproportionation)
    df["target"] = df["target"].str.split(";")
    df = df.explode("target")

    return df
