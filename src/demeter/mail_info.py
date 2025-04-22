"""Mail info method"""

import pandas as pd

from demeter.fetch.mailbox import AnytimeMailbox
from demeter.utils import get_config, save_df_result


def get_anytime_mail_list(country: str, state: str) -> pd.DataFrame:
    """
    Get anytime mail list
    """
    try:
        headers = {"referer": "https://www.anytimemailbox.com/locations"}
        mailbox_list = AnytimeMailbox(headers=headers)
        anytime_mailbox_list = mailbox_list.get_anytime_mailbox_list(
            country=country, state=state
        )

        if len(anytime_mailbox_list) == 0:
            raise ValueError("list is empty")

        df = pd.DataFrame(anytime_mailbox_list)
        df["country"] = country
        df["state"] = state
        return df
    except Exception as e:
        print(f"Error: {e}")
        raise


def get_anytime_mail_detail(detail_domain: str) -> dict:
    """
    Get anytime mail detail
    """
    try:
        headers = {"referer": "https://www.anytimemailbox.com/locations"}
        mailbox_list = AnytimeMailbox(headers=headers)
        anytime_mailbox_detail = mailbox_list.get_anytime_mailbox_detail(
            detail_domain=detail_domain
        )
        return anytime_mailbox_detail
    except Exception as e:
        print(f"Error: {e}")
        return {
            "functions": None,
            "carriers": None,
        }


def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 100) -> list:
    """
    Chunk dataframe
    """
    if len(df) < chunk_size:
        return [df]
    return [df[i : i + chunk_size] for i in range(0, len(df), chunk_size)]


def anytime_mail_result(country: str, state: str) -> pd.DataFrame | None:
    """
    Get anytime mail result
    """
    try:
        mail_list_df = get_anytime_mail_list(country=country, state=state)
        if len(mail_list_df) >= 100:
            chunks = chunk_dataframe(mail_list_df)
        else:
            chunks = [mail_list_df]

        processed_chunks = []
        for chunk in chunks:
            chunk_copy = chunk.copy()
            details = chunk_copy["detail_domain"].apply(get_anytime_mail_detail)
            chunk_copy[["functions", "carriers"]] = pd.DataFrame(
                details.tolist(), index=chunk_copy.index
            )
            processed_chunks.append(chunk_copy)

        return pd.concat(processed_chunks)
    except ValueError as e:
        print(f"Error: {e}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise


def main(mail_provider: str):
    """
    Main entrance
    """
    config = get_config()
    states = ""
    func = None

    if mail_provider == "anytime":
        states = config["MailBox"]["anytime_state"]
        func = anytime_mail_result
    elif mail_provider == "test":
        states = "alaska"
        func = anytime_mail_result

    for state in states.split(","):
        result = func(country="usa", state=state)
        save_df_result(
            df=result,
            save_type="csv",
            save_params={"table_name": f"{mail_provider}_mail_info_{state}.csv"},
        )
