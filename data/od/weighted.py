from tqdm import tqdm
import pandas as pd
import numpy as np
import simpledbf

"""
Transforms absolute OD flows from French census into a weighted destination
matrix given a certain origin commune for work and education.

Remarks: OD for education is assumed to be the same as OD_work due to lack of data
"""

def configure(context):
    context.stage("data.od.cleaned")
    context.stage("data.spatial.codes")
    context.stage("synthesis.locations.work")

def fix_origins(df, commune_ids, purpose):
    existing_ids = set(np.unique(df["origin_id"]))
    missing_ids = commune_ids - existing_ids

    rows = []
    for origin_id in missing_ids:
        for destination_id in commune_ids:
            rows.append((origin_id, destination_id, 1 if origin_id == destination_id else 0))
            #rows.append((origin_id, destination_id, 1.0 if origin_id == destination_id else 0.0))

    print("Fixing %d origins for %s" % (len(missing_ids), purpose))

    return pd.concat([df, pd.DataFrame.from_records(
        rows, columns = ["origin_id", "destination_id", "weight"]
    )])

def execute(context):
    df_codes = context.stage("synthesis.locations.work")
    commune_ids = set(df_codes["commune_id"].unique())

    # Load data
    df_work = context.stage("data.od.cleaned")

    # Add missing origins
    df_work = fix_origins(df_work, commune_ids, "work")

    # Compute totals
    df_total = df_work[["origin_id", "weight"]].groupby("origin_id").sum().reset_index().rename({ "weight" : "total" }, axis = 1)
    df_work = pd.merge(df_work, df_total, on = "origin_id")

    # Compute weight
    df_work["weight"] /= df_work["total"]

    del df_work["total"]

    # Copy work OD to education OD
    df_education = df_work

    print(len(df_work['origin_id'].unique()))

    return df_work, df_education
