import pandas as pd

from elektrapy import PATHWAY_NODES_MAP


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

    # Set index to avoid errors while assigning presence/absence
    df = df.set_index(group_var)
    df = _get_presence(df)

    return df


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


def _get_presence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auxiliary function for getting the presence/absence dataframe.
    """

    df[df > 1] = 1

    return df
