import pandas as pd
import requests
import time

from pathlib import Path
from scripts.utils import flatten_dict


KEY_PATH = Path(Path.cwd()).parent / "keys"


def _get_api_key() -> str:
    """
    Get the College Scorecard API key from the keys file
    """
    with open(KEY_PATH / "data_gov_api.txt", "r") as file:
        return file.readline().strip()


def get_scorecards_by_state(state: str = "CA") -> list[dict]:
    """
    Sends a `GET` request to the College Scorecard API to retrieve a list of
    colleges in a given state.

    :param state: The state to retrieve colleges from. Defaults to "CA".
    :return list: A list of dictionaries containing the college data.
    """

    url = "https://api.data.gov/ed/collegescorecard/v1/schools"
    params = {
        "api_key": _get_api_key(),
        "school.state": state,
        "page": 1,
        "per_page": 100,
    }

    time.sleep(1)
    response = requests.get(url, params=params)
    print(response.json()["metadata"])
    data = response.json()

    number_of_pages = (
        data["metadata"]["total"] // data["metadata"]["per_page"] + 1
    )

    for page in range(2, number_of_pages + 1):
        time.sleep(1)
        params["page"] = page
        response = requests.get(url, params=params)
        print(response.json()["metadata"])
        data["results"] += response.json()["results"]

    return data["results"]


def get_latest_student_scorecard_data_by_state(
        state: str = "CA"
    ) -> pd.DataFrame:
    """
    Get the latest information for colleges in a given state from the College
    Scorecard API

    :param state: The state to retrieve colleges from. Defaults to "CA".
    :return: A DataFrame containing the latest information for colleges in the
        specified state
    """
    data = get_scorecards_by_state(state)

    student = pd.DataFrame()
    for college in data:
        df_temp = pd.DataFrame.from_dict(
            flatten_dict(college.get("latest").get("student")), orient="index"
        ).T
        df_temp["college"] = college.get("school").get("name")
        df_temp = df_temp[
            ["college"] + [col for col in df_temp.columns if col != "college"]
        ]
        student = pd.concat([student, df_temp])

    return student
