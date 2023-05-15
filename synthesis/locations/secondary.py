import geopandas as gpd
import numpy as np
import pandas as pd

def configure(context):
    # absolute paths are used here, please change accordingly

    context.config("data_path")
    context.config("activity_path", r"C:\Users\larad\OneDrive\Documenten\school\Leuven\data\poidpy\Activity.shp")

    context.config("data_path")
    context.config("zone_path", r"C:\Users\larad\OneDrive\Documenten\school\Leuven\data\zonal_data\sh_statbel_statistical_sectors_3812_20220101.shp")


def execute(context):
        # Read the shapefiles generated from Poidpy
        activity = gpd.read_file(context.config("activity_path"))[["classifica", "geometry"]]
        activity = activity.rename(columns={
            'classifica': 'activity_type'
        })

        # Reproject CRS
        new_crs = "EPSG:3812"
        activity = activity.to_crs(new_crs)

        # Read the zoning shapefile
        zone = gpd.read_file(context.config("zone_path"))[["CNIS5_2022", "CS01012022", "geometry"]]
        zone = zone.rename(columns={
            'CS01012022': 'iris_id',
            'CNIS5_2022': 'commune_id'
        })

        # Filter the activity layer to look for secondary locations
        secondary_NACE = ["G", "I", "K", "Q", "R"]
        secondary_locations = activity[activity["activity_type"].isin(secondary_NACE)]

        # Join the zone number to the potential locations
        df_locations = gpd.sjoin(secondary_locations, zone, op="within")

        # Drop unnecessary columns
        df_locations = df_locations.drop(columns=['index_right', 'iris_id'])

        # Attach attributes for activity types
        df_locations["offers_leisure"] = df_locations["activity_type"] == "R"
        df_locations["offers_shop"] = df_locations["activity_type"] == "G"
        df_locations["offers_other"] = ~(df_locations["offers_leisure"] | df_locations["offers_shop"])

        # Define identifiers
        df_locations["location_id"] = np.arange(len(df_locations))
        df_locations["location_id"] = "sec_" + df_locations["location_id"].astype(str)

        # Rearrange the column order
        df_locations = df_locations.reindex(columns=["activity_type", "commune_id", "geometry", "offers_leisure", "offers_shop", "offers_other", "location_id"])

        return df_locations