import pandas as pd

from elektrapy import PATHWAY_NODES_MAP


def preprocess_data(
    df: pd.DataFrame,
    group_var: str,
    fn_var: str = "function"
) -> pd.DataFrame:
    """
    Main function for preprocessing functional annotation data (bigecyhmm) 
    and yield a formatted dataframe that can be used in electron flow diagrams.
    """

    assert len(df), "[ERROR] Empty dataframe."
    assert fn_var in df.columns, f"[ERROR] Missing column '{fn_var}'."

    df = df.rename(columns={fn_var: "pathway"})

    return df


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
