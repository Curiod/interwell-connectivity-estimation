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
    logger = logging.getLogger(__name__)
    logger.info('Preprocessing raw data')

    logger.info(Path.joinpath(input_filepath, "Injection_wells.xlsx"))
    df_inj = pd.read_excel(Path.joinpath(input_filepath, "Injection_wells.xlsx"))
    df_inj['group'] = 'I'

    df_prod = pd.read_excel(Path.joinpath(input_filepath, "Production_wells_train.xlsx"))
    df_prod['group'] = 'P'  

    df_prod["water"] = df_prod["Liquid production rate"] - df_prod["Oil production rate"]
    df_prod["watercut"] = df_prod["water"] / df_prod["Liquid production rate"]

    df = pd.concat([df_prod, df_inj])

    rename_dict = {"Well": "cat", "Date": "date", "Oil production rate": "oil", "Liquid production rate": "liquid", 
              "FormationPressure" : "fp","BottomHolePressure" : "bhp", "Injectivity" : "water_inj", "Choke" : "choke"}
    df.rename(columns=rename_dict, inplace=True)

    path = Path.joinpath(output_filepath, "well_data.csv")
    df.to_csv(path, index=False)

    # create coords dataframe
    df_coords = pd.read_excel(Path.joinpath(input_filepath, "Well_coordinates.xlsx"))
    rename_dict = {"Well": "cat", "X coordinate": "x", "Y coordinate": "y"}
    df_coords.rename(columns=rename_dict, inplace=True)

    path = Path.joinpath(output_filepath,"coords.csv")
    df_coords.to_csv(path, index=False)


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    main()
