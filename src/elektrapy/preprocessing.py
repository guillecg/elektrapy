import pandas as pd

from elektrapy import PATHWAY_NODES_MAP


def _get_nodes(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Auxiliary function for parsing the results and getting both the source 
    and target nodes as well as their corresponding biogeochemical cycle.
    """

    # Add cycle
    results_df["cycle"] = results_df["pathway"]\
        .str.split("-")\
        .str[0]\
        .map({
            "C": "carbon",
            "N": "nitrogen",
            "O": "other",
            "S": "sulfur"
        })

    # Add sources and targets (i.e. substrates and products)
    results_df[["source", "target"]] = results_df["pathway"]\
        .replace(PATHWAY_NODES_MAP)\
        .str.split(" -> ", expand=True)

    # Drop pathways without sources or targets (i.e. not mapped)
    results_df = results_df.dropna(subset="source")
    results_df = results_df.dropna(subset="target")

    # Explode multiple sources (e.g. methanogenesis)
    results_df["source"] = results_df["source"].str.split(";")
    results_df = results_df.explode("source")

    # Explode multiple targets (e.g. from disproportionation)
    results_df["target"] = results_df["target"].str.split(";")
    results_df = results_df.explode("target")

    return results_df
