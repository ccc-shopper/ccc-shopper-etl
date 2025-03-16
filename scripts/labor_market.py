"""
This module contains the functions used to download California labor market
employment projection data from the California Employment Development
Department (EDD) API.

Source:
https://data.ca.gov/organization/california-employment-development-department
"""

import pandas as pd
import requests

SQL_URL = "https://data.ca.gov/api/3/action/datastore_search_sql"
CA_LABOR_MARKET_DATA = {
    "occupation": "274e273c-d18c-4d84-b8df-49b4d13c14ce",
    "industry": "5642307f-30c2-4ddb-b811-507b338e0b4d",
}


def _clean_sql(sql: str) -> str:
    """
    Helper function to clean SQL queries for requests to the CA Open Data Portal
    """
    return " ".join(sql.replace("\n", " ").split())


def _labor_market_sql_to_dataframe(sql: str) -> pd.DataFrame:
    """
    Executes a SQL query against the CA Open Data Portal and converts the
    result set to a DataFrame

    :param sql: The SQL query to execute
    :return: A DataFrame containing the results of the query
    """
    try:
        response = requests.get(SQL_URL, params={"sql": _clean_sql(sql)})
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error raised with SQL:\n{sql}\nError message: {e}")
        return pd.DataFrame()

    try:
        data = response.json()
    except ValueError as e:
        print(f"Error parsing JSON with SQL:\n{sql}\nError message: {e}")
        data = {}

    return pd.DataFrame(data.get("result", {}).get("records", {}))


def get_labor_market_data_dictionary(data_type: str) -> pd.DataFrame:
    """
    Get the data dictionary for the specified data type from the CA Open Data
    Portal

    :param data_type: Either "occupation" or "industry"
    :return: A DataFrame containing the data dictionary
    """
    base_url = "https://data.ca.gov/dataset/"
    if data_type == "occupation":
        base_url += "long-term-occupational-employment-projections/resource/"
    elif data_type == "industry":
        base_url += "long-term-industry-employment-projections/resource/"
    else:
        raise ValueError(
            "Invalid data type. Must be either 'occupation' or 'industry'."
        )
    resource_id = CA_LABOR_MARKET_DATA[data_type]
    url = f"{base_url}{resource_id}"
    return pd.read_html(url)[0]


def get_labor_market_msa_data() -> pd.DataFrame:
    """
    Returns a DataFrame of all Metropolitan Statistical Areas (MSAs) in the
    labor market data.
    """
    sql = f""" 
        SELECT DISTINCT
            "Area Name"
        FROM
            "{CA_LABOR_MARKET_DATA['occupation']}"
        WHERE
            "Area Type" = 'Metropolitan Area'
    """

    msa = _labor_market_sql_to_dataframe(sql)

    # Split the column into more usable information
    msa[["Metropolitan Statistical Area", "MSA Counties"]] = msa[
        "Area Name"
    ].str.extract(r"^(.*) \((.*)\)$")

    return msa


def get_all_soc_detailed_occupations() -> pd.DataFrame:
    """
    Returns a DataFrame of all SOC Level 4 occupations in the labor market data.
    """
    sql = f""" 
        SELECT DISTINCT
            "Standard Occupational Classification (SOC)",
            "Occupational Title"
        FROM
            "{CA_LABOR_MARKET_DATA['occupation']}"
        WHERE
            "SOC Level" = 4
    """

    return (
        _labor_market_sql_to_dataframe(sql)
        .sort_values(by="Standard Occupational Classification (SOC)")
        .reset_index(drop=True)
    )


def get_occupation_projections_by_title(job_title_contains: str) -> pd.DataFrame:
    """
    Returns a DataFrame of labor market occupation projections for all SOC Level
    4 occupations with a title containing the given string.

    :param job_title_contains: The string to search for in the occupation title.
    :return: A DataFrame of labor market occupation projections for all
        occupations with a title containing the given string, ranked ascending
        by SOC Code and descending by Percent Change.
    """

    job_title_contains = job_title_contains.lower()
    sql = f""" 
        SELECT
            *
        FROM
            "{CA_LABOR_MARKET_DATA['occupation']}"
        WHERE
            "SOC Level" = 4
            AND LOWER("Occupational Title") LIKE '%{job_title_contains}%'
            AND "Area Type" = 'Metropolitan Area'
    """

    df = _labor_market_sql_to_dataframe(sql)

    df[
        [
            "Base Year Employment Estimate",
            "Projected Year Employment Estimate",
            "Numeric Change",
            "Percentage Change",
            "Exits",
            "Transfers",
            "Total Job Openings",
            "Median Hourly Wage",
            "Median Annual Wage",
        ]
    ] = df[
        [
            "Base Year Employment Estimate",
            "Projected Year Employment Estimate",
            "Numeric Change",
            "Percentage Change",
            "Exits",
            "Transfers",
            "Total Job Openings",
            "Median Hourly Wage",
            "Median Annual Wage",
        ]
    ].astype(float)

    return df.sort_values(
        by=["Standard Occupational Classification (SOC)", "Percentage Change"],
        ascending=[True, False],
    ).reset_index(drop=True)


def get_occupation_projections_for_msa_and_soc(
    area: str | None = None, soc: str | None = None
) -> pd.DataFrame:
    """
    Returns a DataFrame of labor market occupation projections for a given MSA
    and SOC code at the detailed occupation level.

    :param area: The name of the Metropolitan Statistical Area (MSA) to get
        occupation projections for.
    :param soc: The Standard Occupational Classification (SOC) code to get
        occupation projections for (format `'dd-dddd'`).
    :return: A DataFrame of labor market occupation projections for the given
        MSA and SOC code.
    """
    sql = f""" 
        SELECT
            *
        FROM
            "{CA_LABOR_MARKET_DATA['occupation']}"
        WHERE
            "SOC Level" = 4"""

    if area:
        sql += f" AND \"Area Name\" = '{area}'"
    if soc:
        sql += f" AND \"Standard Occupational Classification (SOC)\" = '{soc}'"
    return _labor_market_sql_to_dataframe(sql).sort_values(
        by=["Area Name", "Standard Occupational Classification (SOC)"]
    )


def _get_top_occupation_per_msa(sort_by: str) -> pd.DataFrame:
    """
    Returns a DataFrame of the top occupation projections for each MSA.

    :param sort_by: The column to sort occupation projections sort_by. Must be
        one of "Percentage Change" or "Numeric Change".
    :return: A DataFrame of the top occupation projections for each MSA.
    """
    sql = f"""
        SELECT
            *
        FROM
            "{CA_LABOR_MARKET_DATA['occupation']}" AS t1
        WHERE
            t1."SOC Level" = 4
            AND t1."Area Type" = 'Metropolitan Area'
            AND t1."{sort_by}" = (
                SELECT
                    t2."{sort_by}"
                FROM
                    "{CA_LABOR_MARKET_DATA['occupation']}" AS t2
                WHERE
                    t2."Area Name" = t1."Area Name"
                    AND t2."SOC Level" = 4
                    AND t2."Area Type" = 'Metropolitan Area'
                ORDER BY
                    t2."{sort_by}" DESC
                LIMIT 1
            )
        ORDER BY
            "Area Name"
    """

    return _labor_market_sql_to_dataframe(sql)


def get_top_occupation_per_msa_by_percentage_change() -> pd.DataFrame:
    """
    Returns a DataFrame of the top occupation projections for each MSA sorted by"
    "Percentage Change".
    """
    return _get_top_occupation_per_msa("Percentage Change")


def get_top_occupation_per_msa_by_numeric_change() -> pd.DataFrame:
    """
    Returns a DataFrame of the top occupation projections for each MSA sorted by
    "Numeric Change".
    """
    return _get_top_occupation_per_msa("Numeric Change")
