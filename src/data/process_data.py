import os
import click
import pandas as pd
import numpy as np


def load_data(qb_filepath: str, rb_filepath: str, wr_filepath: str, te_filepath: str) -> pd.DataFrame:
    """
    Loads each positional dataframe and sets the position
    in a column.

    Arguments:
        qb_filepath (str): Filepath to Quarterback data file.
        rb_filepath (str): Filepath to Running back data file.
        wr_filepath (str): Filepath to Wide Receiver data file.
        te_filepath (str): Filepath to Tight End data file.
    
    Returns:
        pd.DataFrame: DataFrame that combines all of the source 
                      files w/ positions assigned.

    """

    qb_data = pd.read_csv(qb_filepath)
    rb_data = pd.read_csv(rb_filepath)
    wr_data = pd.read_csv(wr_filepath)
    te_data = pd.read_csv(te_filepath)

    qb_data['position'] = 'QB'
    rb_data['position'] = 'RB'
    wr_data['position'] = 'WR'
    te_data['position'] = 'TE'

    data = pd.concat((qb_data, rb_data, wr_data, te_data), axis=0)
    data.columns = data.columns.str.lower()
    data.reset_index(drop=True, inplace=True)
    data['$'] = data['$'].str.replace('$', '')
    data['$'] = data['$'].astype(int)
    data.drop(['dynasty', 'markers', 'bye week'], axis=1, inplace=True)
    data['risk'] = (data['risk'] - data['risk'].min()) / (data['risk'].max() - data['risk'].min())
    return data


def remove_other_keepers(list_of_keepers_names: list, data: pd.DataFrame) -> pd.DataFrame:
    """
    Removes keepers from the dataset based on their names.

    Arguments:
        list_of_keepers_names (list): List of keepers first and last names.
        data (pd.DataFrame): DataFrame containing all of the positional data.

    Returns:
        pd.DataFrame: data minus the keepers listed.

    """
    assert data[data['name'].isin(list_of_keepers_names)].count()[0] == len(list_of_keepers_names), f'Invalid keepers submitted.'

    data = data[~data['name'].isin(keepers)]



@click.command()
@click.option('--qb_filepath', default="../data/qb_udk.csv", help='Filepath to QB data file.')
@click.option('--rb_filepath', default="../data/rb_udk.csv", help='Filepath to RB data file.')
@click.option('--wr_filepath', default="../data/wr_udk.csv", help='Filepath to WR data file.')
@click.option('--te_filepath', default="../data/te_udk.csv", help='Filepath to TE data file.')
@click.option('--processed_filepath', default="../data/processed/processed_data.xlsx", help='Filepath to store the resulting processed file.')
def process_data(start_year: int, end_year: int, data_filepath: str):
    """
    Downloads, processes, and saves NFL data.
    Arguments:
        start_year (int): The first year to pull data from.
        end_year (int): The last year to pull data from.
    Returns:
        None: None.
    """


    data['points_per_dollar'] = round(data['points'] / data['$'], 3)
    data['risk_adjusted_points_per_dollar'] = round(data['points_per_dollar'] * data['risk'], 3)

    rb_data = data[
        data['position'] == 'RB'
    ][['name', '$', 'tier', 'points', 'points_per_dollar', 'risk_adjusted_points_per_dollar']].sort_values(by=['tier', 'risk_adjusted_points_per_dollar'], ascending=[True, False])

    wr_data = data[
        data['position'] == 'WR'
    ][['name', '$', 'tier', 'points', 'points_per_dollar', 'risk_adjusted_points_per_dollar']].sort_values(by=['tier', 'risk_adjusted_points_per_dollar'], ascending=[True, False])

    te_data = data[
        data['position'] == 'TE'
    ][['name', '$', 'tier', 'points', 'points_per_dollar', 'risk_adjusted_points_per_dollar']].sort_values(by=['tier', 'risk_adjusted_points_per_dollar'], ascending=[True, False])

    qb_data = data[
        data['position'] == 'QB'
    ][['name', '$', 'tier', 'points', 'points_per_dollar', 'risk_adjusted_points_per_dollar']].sort_values(by=['tier', 'risk_adjusted_points_per_dollar'], ascending=[True, False])

    
    with pd.ExcelWriter('../data/processed/processed_data.xlsx') as writer1:
        qb_data.to_excel(writer1, sheet_name = 'QB', index = False)
        rb_data.to_excel(writer1, sheet_name = 'RB', index = False)
        wr_data.to_excel(writer1, sheet_name = 'WR', index = False)
        te_data.to_excel(writer1, sheet_name = 'TE', index = False) 

