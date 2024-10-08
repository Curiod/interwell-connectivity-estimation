# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
import pandas as pd


@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    path_to_raw_data = Path(input_filepath)
    path_to_processed_data = Path(output_filepath)

    logger = logging.getLogger(__name__)
    logger.info('Preprocessing raw data')

    df_inj = pd.read_excel(Path.joinpath(path_to_raw_data, "Injection_wells.xlsx"))
    df_inj['group'] = 'I'

    df_prod = pd.read_excel(Path.joinpath(path_to_raw_data, "Production_wells_train.xlsx"))
    df_prod['group'] = 'P'  

    df_prod["water"] = df_prod["Liquid production rate"] - df_prod["Oil production rate"]
    df_prod["watercut"] = df_prod["water"] / df_prod["Liquid production rate"]

    df = pd.concat([df_prod, df_inj])

    # rename columns
    rename_dict = {"Well": "cat", "Date": "date", "Oil production rate": "oil", "Liquid production rate": "liquid", 
              "FormationPressure" : "fp","BottomHolePressure" : "bhp", "Injectivity" : "water_inj", "Choke" : "choke"}
    df.rename(columns=rename_dict, inplace=True)

    # fill nans
    cats = df['cat'].unique()
    groups = ['P', 'I']
    for group in groups:
        for cat in cats:
            well = df.loc[(df['cat'] == cat) & (df['group'] == group)]
            if (well.empty):
                continue
            df.loc[(df['cat'] == cat) & (df['group'] == group)] = fill_nan(well, group)
            
    path = Path.joinpath(path_to_processed_data, "well_data.csv")
    df.to_csv(path, index=False)

    # create coords dataframe
    df_coords = pd.read_excel(Path.joinpath(path_to_raw_data, "Well_coordinates.xlsx"))
    rename_dict = {"Well": "cat", "X coordinate": "x", "Y coordinate": "y"}
    df_coords.rename(columns=rename_dict, inplace=True)

    path = Path.joinpath(path_to_processed_data,"coords.csv")
    df_coords.to_csv(path, index=False)


dict_fillna = {'P': ['bhp', 'fp'], 'I': ['choke', 'fp']}

def fill_nan(df: pd.DataFrame, group) -> pd.DataFrame:
    new_df = df.copy()
    for col in dict_fillna.get(group):
        series = new_df.loc[:, col]
        ref = series.loc[series.first_valid_index()]
        if np.isnan(ref) and (col == 'fp'):
            print("cringe")
        for i, val in series.items():
            if np.isnan(val):
                series.update(pd.Series([ref], index = [i]))
            else:
                ref = val
    return new_df

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
