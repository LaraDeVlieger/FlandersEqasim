import geopandas as gpd
import numpy as np
import pandas as pd


def configure(context):
    # absolute paths are used here, please change accordingly

    context.config("data_path")
    context.config("residential_path", "poidpy/Residential.shp")

    context.config("data_path")
    context.config("zone_path", "zonal_data/sh_statbel_statistical_sectors_3812_20220101.shp")

    context.stage("data.spatial.iris")

def execute(context):
        # Read the shapefiles generated from Poidpy
        residential = gpd.read_file("%s/%s" % (context.config("data_path"), context.config("residential_path")))[["classifica", "geometry"]]
        residential = residential.rename(columns={
            'classifica': 'Type'
        })

        # Reproject CRS
        new_crs = "EPSG:3812"
        residential = residential.to_crs(new_crs)

        # Read the zoning shapefile
        zone = gpd.read_file("%s/%s" % (context.config("data_path"), context.config("zone_path")))[["CNIS5_2022", "CS01012022", "geometry"]]
        zone = zone.rename(columns={
            'CS01012022': 'iris_id',
            'CNIS5_2022': 'commune_id'
        })

        # Join the zone number to the potential locations
        df_addresses = gpd.sjoin(residential, zone, op="within")

        # Drop unnecessary columns
        df_addresses = df_addresses.drop(columns=['index_right', 'Type'])


        # Find required IRIS
        df_iris = context.stage("data.spatial.iris")
        required_iris = set(df_iris["iris_id"].unique())


        # Add fake homes for IRIS without addresses
        missing_iris = required_iris - set(df_addresses["iris_id"].unique())

        print("Adding homes at the centroid of %d/%d IRIS without Poidpy observations" % (
            len(missing_iris), len(required_iris)))

        df_added = []

        for iris_id in missing_iris:
            centroid = df_iris[df_iris["iris_id"] == iris_id]["geometry"].centroid.iloc[0]

            df_added.append({
                "iris_id": iris_id, "geometry": centroid,
                "commune_id": iris_id[:5]
            })

        df_added = pd.DataFrame.from_records(df_added)

        # Merge together
        df_addresses["fake"] = False
        df_added["fake"] = True

        df_addresses = pd.concat([df_addresses, df_added])


        # Add home identifier
        df_addresses["location_id"] = np.arange(len(df_addresses))
        df_addresses["location_id"] = "home_" + df_addresses["location_id"].astype(str)

        # Rearrange the column order
        df_addresses = df_addresses.reindex(columns=["location_id", "iris_id", "commune_id", "fake", "geometry"])

        return df_addresses[["location_id", "iris_id", "commune_id", "fake", "geometry"]]