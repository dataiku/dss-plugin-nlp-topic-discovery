# -*- coding: utf-8 -*-
"""Module to write to partitioned Dataiku folders"""

from typing import List, Dict, AnyStr

import dataiku

TIME_DIMENSION_PATTERNS = {"DKU_DST_YEAR": "%Y", "DKU_DST_MONTH": "%M", "DKU_DST_DAY": "%D", "DKU_DST_HOUR": "%H"}


def get_partition_root(dataset: dataiku.Dataset) -> AnyStr:
    """Retrieve the partition root path using a dataiku.Dataset

    Args:
        dataset (dataiku.Dataset): Input or output dataset of the recipe used to retrieve the partition path pattern

    Returns:
        Partition path or None if dataset is not partitioned

    """
    dku_flow_variables = dataiku.get_flow_variables()
    file_path_pattern = dataset.get_config().get("partitioning").get("filePathPattern", None)
    if file_path_pattern is None:
        return None
    dimensions = get_dimensions(dataset)
    partitions = get_partitions(dku_flow_variables, dimensions)
    file_path = complete_file_path_pattern(file_path_pattern, partitions, dimensions)
    file_path = complete_file_path_time_pattern(dku_flow_variables, file_path)
    return file_path


def get_dimensions(dataset: dataiku.Dataset) -> List:
    """Retrieve the list of partition dimension names

    Args:
        dataset (dataiku.Dataset)

    Returns:
        List of dimensions

    """
    dimensions_dict = dataset.get_config().get("partitioning").get("dimensions")
    dimensions = []
    for dimension in dimensions_dict:
        dimensions.append(dimension.get("name"))
    return dimensions


def get_partitions(dku_flow_variables: Dict, dimensions: List) -> List:
    """Retrieve the list of partition values corresponding to the partition dimensions

    Args:
        dku_flow_variables (dict): Dictionary of flow variables for a project
        dimensions (list): List of partition dimensions

    Raises:
        ValueError: If a 'DKU_DST_$DIMENSION' is not in dku_flow_variables

    Returns:
        List of partitions

    """
    partitions = []
    for dimension in dimensions:
        partition = dku_flow_variables.get("DKU_DST_{}".format(dimension))
        if partition is None:
            raise ValueError(
                "Partition dimension '{}' not found in output.\
                     Make sure the output has the same partitioning as the input".format(
                    dimension
                )
            )
        partitions.append(partition)
    return partitions


def complete_file_path_pattern(file_path_pattern: AnyStr, partitions: List, dimensions: List) -> AnyStr:
    """Fill the placeholders of the partition path pattern for the discrete dimensions with the right partition values

    Args:
        file_path_pattern (str)
        partitions (list): List of partition values corresponding to the partition dimensions
        dimensions (list): List of partition dimensions

    Returns:
        File path prefix. Time dimensions pattern are not filled

    """
    file_path = file_path_pattern.replace(".*", "")
    for partition, dimension in zip(partitions, dimensions):
        file_path = file_path.replace("%{{{}}}".format(dimension), partition)
    return file_path


def complete_file_path_time_pattern(dku_flow_variables: Dict, file_path_pattern: AnyStr) -> AnyStr:
    """Fill the placeholders of the partition path pattern for the time dimensions with the right partition values

    Args:
        dku_flow_variables (dict): Dictionary of flow variables for a project
        file_path_pattern (str)

    Returns:
        File path prefix

    """
    file_path = file_path_pattern
    for time_dimension in TIME_DIMENSION_PATTERNS:
        time_value = dku_flow_variables.get(time_dimension)
        if time_value is not None:
            time_pattern = TIME_DIMENSION_PATTERNS.get(time_dimension)
            file_path = file_path.replace(time_pattern, time_value)
    return file_path
