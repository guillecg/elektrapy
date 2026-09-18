import itertools

import pandas as pd

from elektrapy import PATHWAY_NODE_MAP


def preprocess_data(
    df: pd.DataFrame,
    group_var: str,
    fn_var: str = "function",
    mapping: dict = None
) -> pd.DataFrame:
    """
    Main function for preprocessing functional annotation data (bigecyhmm) 
    and yield a formatted dataframe that can be used in electron flow diagrams.
    """

    assert len(df), "[ERROR] Empty dataframe."
    assert fn_var in df.columns, f"[ERROR] Missing column '{fn_var}'."

    group_var_choices = ["genome_id", "sample_id"]
    assert group_var in group_var_choices, \
        f"[ERROR] Group var must be in {group_var_choices}"

    df = df.rename(columns={fn_var: "pathway"})

    df = _get_transposed(df=df)

    if group_var == "sample_id":
        assert len(mapping.values()), "[ERROR] Empty mapping."
        df = _map_sample_genome(
            df=df,
            mapping=mapping
        )

    df = _get_grouped_counts(
        df=df,
        group_var=group_var
    )

    return df


def get_network_df(
    results_df: pd.DataFrame,
    group_var: str
) -> pd.DataFrame:

    network_df = results_df\
        .melt(id_vars=group_var)\
        .sort_values(group_var)

    # Drop pathways without presence
    network_df = network_df[network_df["value"] >= 1]

    # Extract nodes from "pathway" column
    network_df = _get_nodes_inferred(
        network_df=network_df,
        group_var=group_var
    )

    return network_df


def _map_sample_genome(
    df: pd.DataFrame,
    mapping: dict
) -> pd.DataFrame:
    """
    Auxiliary function for mapping genomes to their corresponding samples.
    """

    df["sample_id"] = df["genome_id"].map(mapping)

    # Drop genome_id column to avoid downstream errors
    df = df.drop("genome_id", axis=1)

    return df


def _get_transposed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auxiliary function for transposing the original count dataframe to get 
    genomes (index) per function (columns).
    """
    return df\
        .set_index("pathway").T\
        .reset_index()\
        .rename(columns={"index": "genome_id"})


def _get_grouped_counts(
    df: pd.DataFrame,
    group_var: str
) -> pd.DataFrame:
    """
    Auxiliary function for grouping the counts according to either genome or 
    sample IDs.
    """
    return df\
        .groupby(group_var, as_index=False)\
        .sum()


def _get_nodes(network_df: pd.DataFrame) -> pd.DataFrame:
    """
    Auxiliary function for parsing the network dataframe and getting both the 
    source and target nodes as well as their corresponding biogeochemical cycle.
    """

    assert len(network_df), "[ERROR] Empty dataframe."

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
        .replace(PATHWAY_NODE_MAP)\
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


def _get_nodes_inferred(
    network_df: pd.DataFrame,
    group_var: str
) -> pd.DataFrame:
    """
    Auxiliary function for parsing the network dataframe and getting both the 
    source and target nodes as well as their corresponding biogeochemical cycle.
    The nodes are inferred according to the presence of oxidation and reduction
    reactions.
    """

    assert len(network_df), "[ERROR] Empty dataframe."

    network_df["node"] = network_df["pathway"].map(PATHWAY_NODE_MAP)
    network_df[["node_type", "node"]] = network_df["node"]\
        .str.split("-", expand=True)
    network_df["node_type"] = network_df["node_type"].replace({
        "oxidation": "source",
        "reduction": "target",
        "fixation": "target"
    })

    network_df_infer = []

    for record_id in network_df[group_var].unique():
        record_df = network_df[network_df[group_var] == record_id].copy()

        # Create node combinations (donor to acceptor)
        redox_combinations = list(itertools.product(
            record_df[record_df["node_type"] == "source"]["node"].unique(),
            record_df[record_df["node_type"] == "target"]["node"].unique()
        ))

        # Remove pairs with the same node
        redox_combinations = [
            pair for pair in redox_combinations
            if pair[0] != pair[1]
        ]

        # Create entry for the given record
        record_df = pd.DataFrame(
            redox_combinations,
            columns=["source", "target"]
        )
        record_df[group_var] = record_id
        record_df["value"] = 1

        network_df_infer.append(
            record_df[[group_var, "source", "target", "value"]]
        )

    return pd.concat(network_df_infer)
