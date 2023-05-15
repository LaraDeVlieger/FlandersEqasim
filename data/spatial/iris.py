import pandas as pd
import geopandas as gpd
import os

"""
Loads the IRIS zoning system.
"""

"Elle: Changed path to new zoning file."

def configure(context):
    context.config("data_path")
    context.config("iris_path", "zonal_data/sh_statbel_statistical_sectors_3812_20220101.shp")
    context.stage("data.spatial.codes")

"Elle: Changed names of columns and EPSG"
def execute(context):
    df_codes = context.stage("data.spatial.codes")

    df_iris = gpd.read_file("%s/%s" % (context.config("data_path"), context.config("iris_path")))[[
        "CS01012022", "CNIS5_2022", "geometry"
    ]].rename(columns = {
        "CS01012022": "iris_id",
        "CNIS5_2022": "commune_id"
    })

    df_iris.crs = "EPSG:3812"

    df_iris["iris_id"] = df_iris["iris_id"].astype("category")
    df_iris["commune_id"] = df_iris["commune_id"].astype("category")

    # Merge with requested codes and verify integrity

    df_iris["iris_id"] = df_iris["iris_id"].astype(str)
    df_iris["commune_id"] = df_iris["commune_id"].astype(str)
    df_codes["iris_id"] = df_codes["iris_id"].astype(str)
    df_codes["commune_id"] = df_codes["commune_id"].astype(str)
    df_iris = pd.merge(df_iris, df_codes, on = ["iris_id", "commune_id"])

    requested_iris = set(df_codes["iris_id"].unique())
    merged_iris = set(df_iris["iris_id"].unique())

    if requested_iris != merged_iris:
        raise RuntimeError("Some IRIS are missing: %s" % (requested_iris - merged_iris,))

    return df_iris

def validate(context):
    if not os.path.exists("%s/%s" % (context.config("data_path"), context.config("iris_path"))):
        raise RuntimeError("IRIS data is not available")

    return os.path.getsize("%s/%s" % (context.config("data_path"), context.config("iris_path")))
