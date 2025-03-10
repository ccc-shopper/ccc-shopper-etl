"""
This module contains functions for joining data from different sources.
"""

import scripts.cccco as cccco
import scripts.labor_market as labor_market
import scripts.college_scorecard as scorecard

import pandas as pd
import time

from fuzzywuzzy import process


def get_best_match(county: str, choices: list[str]) -> str | None:
    """
    Uses fuzzy matching to find the best match for a given county in a list of
    choices.

    :param county: The county to match.
    :param choices: The list of choices to match against.
    :return: The best match for the county in the list of choices.
    """
    best_match = process.extractOne(county, choices)
    return best_match[0] if best_match else None


# For merging with College TOP Code data:

# These crosswalks are available in the resources folder. They are not easily
# scraped from the web and are very infrequently updated (on the order of
# decades), so I feel manual downloads are a reasonable approach.


def _load_cip_soc_crosswalk() -> pd.DataFrame:
    """
    Loads the CIP - SOC crosswalk data from the resources folder and performs
    the necessary ETL.

    :return: The CIP - SOC crosswalk data.
    """
    cip_soc_crosswalk = pd.read_excel(
        "./resources/CIP2020_SOC2018_Crosswalk.xlsx",
        sheet_name="SOC-CIP",
        dtype=str
    )
    cip_soc_crosswalk["CIP2020Code"] = (
        cip_soc_crosswalk["CIP2020Code"]
        .astype(str)
        .str.replace(r"\D", "", regex=True)
        .astype(str)
    )
    return cip_soc_crosswalk


def _load_top_cip_crosswalk() -> pd.DataFrame:
    """
    Loads the TOP - CIP crosswalk data from the resources folder and performs
    the necessary ETL.

    :return: The TOP - CIP crosswalk data.
    """
    top_cip_crosswalk = pd.read_excel(
        "./resources/TOPCIP2020June26.xlsx",
        header=1,
        dtype=str
    ).drop(columns=["CIP Code (2)"])
    top_cip_crosswalk["TOP Code"] = top_cip_crosswalk["TOP Code"].apply(
        lambda x: (
            x.zfill(4) 
            if "." not in x 
            else x.split(".")[0].zfill(4) + "." + x.split(".")[1]
        )
    )
    top_cip_crosswalk["TOP Code"] = (
        top_cip_crosswalk["TOP Code"]
        .str.replace(r"\D", "", regex=True)
        .str.ljust(6, "0")
    )
    return top_cip_crosswalk


def match_colleges_top_from_soc(soc: str) -> pd.DataFrame:
    """
    Given a Standard Occupation Classification (SOC) Code, retrieves all
    colleges that offer programs in the relevant TOP Codes via the CCCCO API.

    :param soc: The SOC Code to match.
    :return: A DataFrame of colleges that offer programs in the relevant TOP
        Codes.
    """

    try:
        cip_soc_crosswalk = _load_cip_soc_crosswalk()
        top_cip_crosswalk = _load_top_cip_crosswalk()
    except FileNotFoundError:
        print("Unable to locate crosswalks.")
        return pd.DataFrame()

    matched_cip_codes = (
        cip_soc_crosswalk[cip_soc_crosswalk["SOC2018Code"] == soc]
    )

    matched_top_codes = (
        top_cip_crosswalk[
            top_cip_crosswalk["CIP Code"].isin(matched_cip_codes["CIP2020Code"])
        ]
    )

    unique_matched_top_codes = matched_top_codes["TOP Code"].unique()

    colleges_with_matched_top_codes = pd.DataFrame()
    for top_code in unique_matched_top_codes:
        time.sleep(0.25)
        colleges = cccco.get_ccc_programs(top_code)
        colleges_with_matched_top_codes = pd.concat(
            [colleges_with_matched_top_codes, colleges]
        )

    try:
        colleges_with_matched_top_codes = (
            pd.merge(
                colleges_with_matched_top_codes,
                matched_top_codes[
                    [
                        "TOP Code",
                        "TOP Code Title"
                    ]
                ].drop_duplicates(),
                left_on="TopCode",
                right_on="TOP Code",
                how="left",
            )
            .drop(columns=["TOP Code"])
            .rename(columns={"TOP Code Title": "TopCodeTitle"})
            .sort_values(by=["CollegeID", "TopCode"])
            .reset_index(drop=True)
        )
    except Exception as e:
        print(f"Error thrown when attempting SOC-TOP Merge with {soc = }:")
        print(e.__class__.__name__, e)
        return pd.DataFrame()

    return colleges_with_matched_top_codes
