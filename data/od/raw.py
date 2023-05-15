import pandas as pd
import os

"""
Loads raw OD data from census data.
"""

def configure(context):
    context.stage("data.spatial.codes")
    context.config("data_path")
    context.config("od_path", r"C:\Users\larad\OneDrive\Documenten\school\Leuven\data\census2011_od.csv")
    # context.config("od_path", "\poidpy\census2011_od.csv")
    context.stage("synthesis.locations.work")
def iris2commune(string):
    return string[6:11]

def execute(context):
    df_codes = context.stage("synthesis.locations.work")
    requested_communes = df_codes["commune_id"].unique().astype(str)

    df_work = pd.read_csv(context.config("od_path"))

    # iris to commune
    df_work['CD_SECTOR_RESIDENCE'] = df_work['CD_SECTOR_RESIDENCE'].apply(iris2commune)
    df_work['CD_SECTOR_WORK'] = df_work['CD_SECTOR_WORK'].apply(iris2commune)

    # filter the errors
    f = df_work["CD_SECTOR_RESIDENCE"].isin(requested_communes)
    f &= df_work["CD_SECTOR_WORK"].isin(requested_communes)
    df_work = df_work[f]

    return (df_work)
        


