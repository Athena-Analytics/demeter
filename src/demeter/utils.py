"""Utils"""

import base64
import configparser
import os
import sqlite3

import pandas as pd
from sqlalchemy import create_engine

script_path = os.path.realpath(__file__)
working_dir = os.path.dirname(script_path)


def get_config(config_file: str = "config.ini") -> configparser.ConfigParser:
    """
    Get config from local file
    """
    config = configparser.ConfigParser()
    config.read(f"{working_dir}/{config_file}")

    return config


def update_config(
    config: configparser.ConfigParser, config_file: str = "config.ini"
) -> str:
    """
    Update config to local file
    """
    with open(f"{working_dir}/{config_file}", "w", encoding="utf-8") as file:
        config.write(file)

    return "success"


def get_object_path(
    path_type: str,
    file_name: str | None = None,
    dir_name: str = "resources",
    sub_dir: str | None = None,
) -> str:
    """
    Get path of objects
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


def save_df_result(df: pd.DataFrame, save_type: str, save_params: dict):
    """
    Save DataFrame to various exts
    """
    if "path" in save_params:
        path = save_params["path"]
    else:
        path = f"{working_dir}/results"
    table_name = save_params["table_name"]

    try:
        if save_type == "postgresql":
            database_name = save_params["database_name"]
            engine = create_engine(
                "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
            )
            df.to_sql(
                name=table_name,
                con=engine,
                schema="public",
                index=False,
                if_exists="append",
            )
            print(f"save to postgresql-{database_name}-{table_name} successfully")

        elif save_type == "sqlite":
            database_name = save_params["database_name"]
            with sqlite3.connect(f"{path}/{database_name}") as conn:
                df.to_sql(table_name, conn, if_exists="append", index=False)
                conn.commit()
            print(f"save to sqlite-{database_name}-{table_name} successfully")

        elif save_type == "excel":
            df.to_excel(f"{path}/{table_name}", index=False)
            print(f"save {table_name} to excel successfully")

        elif save_type == "csv":
            df.to_csv(f"{path}/{table_name}", index=False, encoding="utf-8")
            print(f"save {table_name} to csv successfully")

        elif save_type == "json":
            df.to_json(
                f"{path}/{table_name}",
                orient="records",
                date_format="iso",
                lines=True,
                index=False,
                mode="a",
            )
            print(f"save {table_name} to json successfully")

        else:
            raise ValueError(
                f"save_type must be sqlite, excel, csv, json. but got {save_type}"
            )
    except Exception as e:
        print(e)
        raise


def encode_base64_str(s: str) -> str:
    """
    Encode str by base64
    """
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")


def decode_base64_str(s: str) -> str:
    """
    Decode str by base64
    """
    return base64.b64decode(s.encode("utf-8") + b"==").decode("utf-8")


if __name__ == "__main__":
    pass
