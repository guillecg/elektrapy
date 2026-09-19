import pytest

import os

import pandas as pd


def test_metadata_df_shape(metadata_df: pd.DataFrame) -> None:
    assert metadata_df.shape == (12, 4), \
        "[ERROR] Incorrect shape for metadata_df."


def test_metadata_df_genome(metadata_df: pd.DataFrame) -> None:
    assert "genome_id" in metadata_df.columns, \
        "[ERROR] 'genome_id' column not in metadata_df."


def test_metadata_df_sample(metadata_df: pd.DataFrame) -> None:
    assert "sample_id" in metadata_df.columns, \
        "[ERROR] 'sample_id' column not in metadata_df."


def test_metadata_df_type(metadata_df: pd.DataFrame) -> None:
    assert "type" in metadata_df.columns, \
        "[ERROR] 'type' column not in metadata_df."


def test_metadata_df_depth(metadata_df: pd.DataFrame) -> None:
    assert "depth" in metadata_df.columns, \
        "[ERROR] 'depth' column not in metadata_df."


def test_pathway_df_shape(pathway_df: pd.DataFrame) -> None:
    assert pathway_df.shape == (40, 13), \
        "[ERROR] Incorrect shape for pathway_df."


def test_pathway_df_function(pathway_df: pd.DataFrame) -> None:
    assert "function" in pathway_df.columns, \
        "[ERROR] 'function' column not in pathway_df."
