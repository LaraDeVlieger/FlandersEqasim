import pandas as pd
import numpy as np

"""
Cleans OD data to arrive at OD flows between municipalities for work

"""

def configure(context):
    context.stage("data.od.raw")
    context.stage("data.spatial.codes")

RENAME = { "CD_SECTOR_RESIDENCE" : "origin_id", "CD_SECTOR_WORK" : "destination_id", "OBS_VALUE" : "weight" }

def execute(context):

    # Load data
    df_work = context.stage("data.od.raw")

    # Renaming
    df_work = df_work.rename(RENAME, axis=1)

    # Aggregate the flows
    df_work = df_work.groupby(['origin_id', 'destination_id'])['weight'].sum().reset_index()
    df_work["weight"] = df_work["weight"].fillna(0.0)

    return df_work
