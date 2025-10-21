"""Utility functions"""

import base64
import configparser
import os
import sqlite3

import pandas as pd

script_path = os.path.realpath(__file__)
working_dir = os.path.dirname(script_path)


def get_config(config_file: str = "config.ini") -> configparser.ConfigParser:
    """
    Get config from local file

    Args:
        config_file (str): Name of the configuration file to read
    Returns:
        configparser.ConfigParser: Config object containing the configuration
    Raises:
        FileNotFoundError: If the configuration file does not exist
        IOError: If there is an error reading the file
        Exception: For any other errors during loading
    """
    try:
        config = configparser.ConfigParser()
        config.read(f"{working_dir}/{config_file}")
        return config
    except FileNotFoundError as e:
        print(f"Configuration file {config_file} not found: {e}")
        raise
    except IOError as e:
        print(f"Error reading configuration file {config_file}: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while loading config: {e}")
        raise


def update_config(
    config: configparser.ConfigParser, config_file: str = "config.ini"
) -> str:
    """
    Update config to local file

    Args:
        config (configparser.ConfigParser): Config object to save
        config_file (str): Name of the configuration file to save
    Returns:
        str: Status message indicating success
    Raises:
        FileNotFoundError: If the configuration file does not exist
        IOError: If there is an error writing to the file
        Exception: For any other errors during saving
    """
    try:
        with open(f"{working_dir}/{config_file}", "w", encoding="utf-8") as file:
            config.write(file)

        return "success"
    except FileNotFoundError as e:
        print(f"Configuration file {config_file} not found: {e}")
        raise
    except IOError as e:
        print(f"Error writing to configuration file {config_file}: {e}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while updating config: {e}")
        raise


def get_object_path(
    path_type: str,
    file_name: str | None = None,
    dir_name: str = "resources",
    sub_dir: str | None = None,
) -> str:
    """
    Get path of objects

    Args:
        path_type (str): Type of path to return (file or dir)
        file_name (str | None): Name of the file, if applicable
        dir_name (str): Name of the directory
        sub_dir (str | None): Subdirectory name, if applicable
    Returns:
        str: Full path to the specified object
    Raises:
        ValueError: If path_type is not 'file' or 'dir'
    """
    if sub_dir is not None:
        new_dir = f"{dir_name}/{sub_dir}"
    else:
        new_dir = dir_name

    if path_type == "dir":
        return f"{working_dir}/{new_dir}"
    if path_type == "file":
        return f"{working_dir}/{new_dir}/{file_name}"

    raise ValueError(f"path_type must be file or dir. but got {path_type}")


def save_df_to_file(df: pd.DataFrame, save_type: str, save_params: dict):
    """
    Save DataFrame to file

    Args:
        df (pd.DataFrame): DataFrame to save
        save_type (str): Type of file to save to (e.g., excel, csv, json)
        save_params (dict): Parameters for saving, including path and file name
    Raises:
        ValueError: If save_type is not recognized
        Exception: If there is an error during saving
    """
    if "path" in save_params:
        path = save_params["path"]
    else:
        path = f"{working_dir}/results"
    file_name = save_params["file_name"]

    try:
        if save_type == "excel":
            df.to_excel(f"{path}/{file_name}", index=False)
        elif save_type == "csv":
            df.to_csv(f"{path}/{file_name}", index=False, encoding="utf-8")
        elif save_type == "json":
            df.to_json(
                f"{path}/{file_name}",
                orient="records",
                date_format="iso",
                lines=True,
                index=False,
                mode="a",
            )
        else:
            raise ValueError(f"save_type must be excel, csv, json. but got {save_type}")

        print(f"save {file_name} to {save_type} successfully")
    except Exception as e:
        print(e)
        raise


def save_df_to_db(df: pd.DataFrame, db_type: str, db_params: dict):
    """
    Save DataFrame to database

    Args:
        df (pd.DataFrame): DataFrame to save
        db_type (str): Type of database to save to (e.g., sqlite)
        db_params (dict): Parameters for saving, including path, database name and table name
    Raises:
        ValueError: If required parameters are missing or if db_type is not recognized
        Exception: If there is an error during saving
    """

    path = db_params.get("path", f"{working_dir}/db")
    database_name = db_params.get("database_name", None)
    table_name = db_params.get("table_name", None)

    try:
        if database_name is None:
            raise ValueError("database_name must be provided in db_params")

        if table_name is None:
            raise ValueError("table_name must be provided in db_params")

        if db_type == "sqlite":
            with sqlite3.connect(f"{path}/{database_name}") as conn:
                df.to_sql(table_name, conn, if_exists="append", index=False)
                conn.commit()
        else:
            raise ValueError(f"db_type must be sqlite. but got {db_type}")

        print(f"save to {db_type}-{database_name}-{table_name} successfully")
    except Exception as e:
        print(e)
        raise


def get_data_from_db(db_type: str, db_params: dict) -> pd.DataFrame:
    """
    Get data from database and save it to DataFrame

    Args:
        db_type (str): Type of database to fetch from (e.g., sqlite)
        db_params (dict): Parameters for fetching, including path, database name and SQL statement
    Returns:
        pd.DataFrame: DataFrame containing the fetched data
    Raises:
        ValueError: If required parameters are missing or if db_type is not recognized
        Exception: If there is an error during fetching
    """
    df = None
    path = db_params.get("path", f"{working_dir}/db")
    database_name = db_params.get("database_name", None)
    sql_statement = db_params.get("sql_statement", None)

    try:
        if database_name is None:
            raise ValueError("database_name must be provided in save_params")

        if sql_statement is None:
            raise ValueError("sql_statement must be provided in save_params")

        if db_type == "sqlite":
            with sqlite3.connect(f"{path}/{database_name}") as conn:
                df = pd.read_sql_query(sql_statement, conn)
        else:
            raise ValueError(f"db_type must be sqlite. but got {db_type}")

        if df is None:
            raise ValueError("DataFrame is None, please check your SQL statement")

        return df
    except Exception as e:
        print(e)
        raise


def encode_base64_str(s: str) -> str:
    """
    Encode str by base64

    Args:
        s (str): String to encode
    Returns:
        str: Base64 encoded string
    """
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")


def decode_base64_str(s: str) -> str:
    """
    Decode str by base64

    Args:
        s (str): Base64 encoded string to decode
    Returns:
        str: Decoded string
    """
    return base64.b64decode(s.encode("utf-8") + b"==").decode("utf-8")
