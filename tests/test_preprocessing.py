import pytest

import os

import pandas as pd

from elektrapy.preprocessing import (
    preprocess_data,
    get_network_df,
    _get_transposed,
    _map_sample_genome,
    _get_grouped_counts
)


@pytest.fixture(scope="module", autouse=False)
def mapping(metadata_df: pd.DataFrame) -> dict:
    yield dict(
        zip(
            metadata_df["genome_id"],
            metadata_df["sample_id"]
        )
    )


def test_preprocess_data_genome(
    pathway_df: pd.DataFrame,
    results_df_genome: pd.DataFrame
) -> None:
    pd.testing.assert_frame_equal(
        left=results_df_genome,
        right=preprocess_data(
            df=pathway_df,
            group_var="genome_id"
        )
    )


def test_preprocess_data_sample(
    pathway_df: pd.DataFrame,
    results_df_sample: pd.DataFrame,
    metadata_df: pd.DataFrame,
    mapping: dict
) -> None:
    pd.testing.assert_frame_equal(
        left=results_df_sample,
        right=preprocess_data(
            df=pathway_df,
            group_var="sample_id",
            mapping=mapping
        )
    )


@pytest.mark.parametrize(("group_var", "mapping"), [
    ("genome_id", None),
    ("sample_id", mapping),
    pytest.param(
        "other",
        None,
        marks=pytest.mark.xfail(reason="Not implemented.")
    ),
    pytest.param(
        "other",
        mapping,
        marks=pytest.mark.xfail(reason="Not implemented.")
    )
], indirect=["mapping"])
def test_preprocess_data_group_var(
    pathway_df: pd.DataFrame,
    group_var: str,
    mapping: dict
) -> None:
    preprocess_data(
        df=pathway_df,
        group_var=group_var,
        mapping=mapping
    )


@pytest.mark.parametrize(("group_var", "fn_var", "mapping"), [
    ("genome_id", "function", None),
    ("sample_id", "function", mapping),
    pytest.param(
        "genome_id",
        "other",
        None,
        marks=pytest.mark.xfail(reason="Column not originally found in data.")
    ),
    pytest.param(
        "sample_id",
        "other",
        mapping,
        marks=pytest.mark.xfail(reason="Column not originally found in data.")
    )
], indirect=["mapping"])
def test_preprocess_data_fn_var(
    pathway_df: pd.DataFrame,
    group_var: str,
    fn_var: str,
    mapping: dict
) -> None:
    results_df_genome = preprocess_data(
        df=pathway_df,
        group_var=group_var,
        fn_var=fn_var,
        mapping=mapping
    )


def test_get_network_df_genome(
    results_df_genome: pd.DataFrame,
    network_df_genome: pd.DataFrame
) -> None:

    network_df = get_network_df(
        results_df=results_df_genome,
        group_var="genome_id"
    )
    network_df = network_df.reset_index(drop=True)

    pd.testing.assert_frame_equal(
        left=network_df_genome,
        right=network_df
    )


def test_get_network_df_sample(
    results_df_sample: pd.DataFrame,
    network_df_sample: pd.DataFrame
) -> None:
    pd.testing.assert_frame_equal(
        left=network_df_sample,
        right=get_network_df(
            results_df=results_df_sample,
            group_var="sample_id"
        )
    )


@pytest.mark.parametrize(("group_var", "fn_var"), [
    ("genome_id", "function"),
    ("sample_id", "function")
])
def test__get_transposed(
    pathway_df: pd.DataFrame,
    data_dir: str,
    group_var: str,
    fn_var: str
) -> None:

    df = pathway_df.copy()

    df = df.rename(columns={fn_var: "pathway"})

    df = _get_transposed(df=df)

    # Remove name from column list
    df.columns.name = None

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"pathway-transposed-{group_var.split('_')[0]}.csv"
            )
        ),
        right=df
    )


@pytest.mark.parametrize(("group_var", "fn_var", "mapping"), [
    ("genome_id", "function", None),
    ("sample_id", "function", mapping)
], indirect=["mapping"])
def test__map_sample_genome(
    pathway_df: pd.DataFrame,
    data_dir: str,
    group_var: str,
    fn_var: str,
    mapping: dict
) -> None:

    df = pathway_df.copy()

    df = df.rename(columns={fn_var: "pathway"})

    df = _get_transposed(df=df)

    if group_var == "sample_id":
        assert len(mapping.values()), "[ERROR] Empty mapping."
        df = _map_sample_genome(
            df=df,
            mapping=mapping
        )

    # Remove name from column list
    df.columns.name = None

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"pathway-mapped-{group_var.split('_')[0]}.csv"
            )
        ),
        right=df
    )


@pytest.mark.parametrize(("group_var", "fn_var", "mapping"), [
    ("genome_id", "function", None),
    ("sample_id", "function", mapping)
], indirect=["mapping"])
def test__get_grouped_counts(
    pathway_df: pd.DataFrame,
    data_dir: str,
    group_var: str,
    fn_var: str,
    mapping: dict
) -> None:

    df = pathway_df.copy()

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

    # Remove name from column list
    df.columns.name = None

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"pathway-counts-{group_var.split('_')[0]}.csv"
            )
        ),
        right=df
    )


def test_get_network_df_prenodes_genome(
    data_dir: str,
    results_df_genome: pd.DataFrame,
    group_var: str = "genome_id"
) -> None:

    results_df = results_df_genome.copy()

    network_df = results_df\
        .melt(id_vars=group_var)\
        .sort_values(group_var)

    # Drop pathways without presence
    network_df = network_df[network_df["value"] >= 1]

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"network-prenodes-{group_var.split('_')[0]}.csv"
            )
        ),
        right=network_df.reset_index(drop=True)
    )


def test_get_network_df_prenodes_sample(
    data_dir: str,
    results_df_sample: pd.DataFrame,
    group_var: str = "sample_id"
) -> None:

    results_df = results_df_sample.copy()

    network_df = results_df\
        .melt(id_vars=group_var)\
        .sort_values(group_var)

    # Drop pathways without presence
    network_df = network_df[network_df["value"] >= 1]

    pd.testing.assert_frame_equal(
        left=pd.read_csv(
            os.path.join(
                data_dir,
                "results",
                f"network-prenodes-{group_var.split('_')[0]}.csv"
            )
        ),
        right=network_df.reset_index(drop=True)
    )
