# -*- coding: utf-8 -*-
"""Module with read/write utility functions based on the Dataiku API"""

from typing import List, AnyStr, Union

import pandas as pd
import numpy as np

import dataiku
import logging


def count_records(dataset: dataiku.Dataset) -> int:
    """Count the number of records of a dataset using the Dataiku dataset metrics API
    Args:
        dataset: dataiku.Dataset instance
    Returns:
        Number of records
    """
    metric_id = "records:COUNT_RECORDS"
    dataset_name = dataset.short_name
    partitions = dataset.read_partitions
    client = dataiku.api_client()
    project = client.get_project(dataiku.default_project_key())
    record_count = 0
    logging.info("Counting records of dataset: {}".format(dataset_name))
    if partitions is None or len(partitions) == 0:
        project.get_dataset(dataset_name).compute_metrics(metric_ids=[metric_id])
        metric = dataset.get_last_metric_values()
        record_count = dataiku.ComputedMetrics.get_value_from_data(metric.get_global_data(metric_id=metric_id))
        logging.info("Dataset contains {:d} records and is not partitioned".format(record_count))
    else:
        for partition in partitions:
            project.get_dataset(dataset_name).compute_metrics(partition=partition, metric_ids=[metric_id])
            metric = dataset.get_last_metric_values()
            record_count += dataiku.ComputedMetrics.get_value_from_data(
                metric.get_partition_data(partition=partition, metric_id=metric_id)
            )
        logging.info("Dataset contains {:d} records in partition(s) {}".format(record_count, partitions))
    return record_count


def clean_empty_list(sequence: List) -> Union[List, AnyStr]:
    """If the input sequence is a valid non-empty list, return list, else an empty string
    Args:
        sequence: Original list
    Returns:
       Original list or empty string
    """
    output = ""
    if isinstance(sequence, list):
        if len(sequence) != 0:
            output = sequence
    return output


def unique_list(sequence: List) -> List:
    """Make a list unique, ordering values by order of appearance in the original list
    Args:
        sequence: Original list
    Returns:
       List with unique elements ordered by appearance in the original list
    """
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


def truncate_text_list(text_list: List[AnyStr], num_characters: int = 140) -> List[AnyStr]:
    """Truncate a list of strings to a given number of characters
    Args:
        text_list: List of strings
        num_characters: Number of characters to truncate each string to
    Returns:
       List with truncated strings
    """
    output_text_list = []
    for text in text_list:
        if len(text) > num_characters:
            output_text_list.append(text[:num_characters] + " (...)")
        else:
            output_text_list.append(text)
    return output_text_list


def clean_text_df(df: pd.DataFrame, dropna_columns: List[AnyStr] = None) -> pd.DataFrame:
    """Clean a pandas.DataFrame containing text columns to get rid of empty strings and NaNs values
    Args:
        df: Input pandas.DataFrame which should contain only text
        dropna_columns: Optional list of column names where empty strings and NaN should be checked
            Default is None, which means that all columns will be checked
    Returns:
       pandas.DataFrame with rows dropped in case of empty strings or NaN values
    """
    for col in df.columns:
        df[col] = df[col].str.strip().replace("", np.NaN)
    if dropna_columns is None:
        df = df.dropna()
    else:
        df = df.dropna(subset=dropna_columns)
    return df


def generate_unique(name: AnyStr, existing_names: List[AnyStr], prefix: AnyStr = None) -> AnyStr:
    """Generate a unique name among existing ones by suffixing a number. Can also add an optional prefix.
    Args:
        name: Input name
        existing_names: List of existing names
        prefix: Optional prefix to add to the output name
    Returns:
       Unique name with a number suffix in case of conflict, and an optional prefix
    """
    if prefix is not None:
        new_name = "{}_{}".format(prefix, name)
    else:
        new_name = name
    for i in range(1, 1001):
        if new_name not in existing_names:
            return new_name
        if prefix is not None:
            new_name = "{}_{}_{}".format(prefix, name, i)
        else:
            new_name = "{}_{}".format(name, i)
    raise RuntimeError("Failed to generated a unique name")


def move_columns_after(df: pd.DataFrame, columns_to_move: List[AnyStr], after_column: AnyStr) -> pd.DataFrame:
    """Reorder columns by moving a list of columns after another column
    Args:
        df: Input pandas.DataFrame
        columns_to_move: List of column names to move
        after_column: Name of the columns to move columns after
    Returns:
       pandas.DataFrame with reordered columns
    """
    after_column_position = df.columns.get_loc(after_column) + 1
    reordered_columns = (
        df.columns[:after_column_position].tolist() + columns_to_move + df.columns[after_column_position:].tolist()
    )
    df.reindex(columns=reordered_columns)
    return df