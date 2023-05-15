import geopandas as gpd
import numpy as np
import pandas as pd

def configure(context):
        #absolute paths are used here, please change accordingly

        context.config("data_path")
        context.config("activity_path", r"C:\Users\Timothy\Desktop\KUL\IP2\Leuven\data\poidpy\Activity.shp")

        context.config("data_path")
        context.config("zone_path", r"C:\Users\Timothy\Desktop\KUL\IP2\Leuven\data\zonal_data\sh_statbel_statistical_sectors_3812_20220101.shp")

        context.stage("data.spatial.municipalities")

def execute(context):

        # Read the shapefiles generated from Poidpy
        activity = gpd.read_file(context.config("activity_path"))[["classifica", "geometry"]]
        activity = activity.rename(columns={
            'classifica': 'NACE'
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

        # Filter the activity layer to look for education locations
        education_NACE = ["P"]
        education_locations = activity[activity["NACE"].isin(education_NACE)]

        # Join the zone number to the potential locations
        df_locations = gpd.sjoin(education_locations, zone, op="within")

        # Drop unnecessary columns
        df_locations = df_locations.drop(columns=['index_right', 'NACE', 'iris_id'])


        # Add education locations to the centroid of zones without any education location
        df_zones = context.stage("data.spatial.municipalities")

        required_communes = set(df_zones["commune_id"].unique())
        missing_communes = required_communes - set(df_locations["commune_id"].unique())

        print("Adding fake education locations for %d/%d municipalities" % (
                len(missing_communes), len(required_communes)
        ))

        df_added = []

        for commune_id in sorted(missing_communes):
                centroid = df_zones[df_zones["commune_id"] == commune_id]["geometry"].centroid.iloc[0]

                df_added.append({
                        "commune_id": commune_id, "geometry": centroid
                })

        df_added = pd.DataFrame.from_records(df_added)

        # Merge together
        df_locations["fake"] = False
        df_added["fake"] = True

        df_locations = pd.concat([df_locations, df_added])


        # Define identifiers
        df_locations["location_id"] = np.arange(len(df_locations))
        df_locations["location_id"] = "edu_" + df_locations["location_id"].astype(str)

        # Rearrange the column order
        df_locations = df_locations.reindex(columns=["location_id", "commune_id", "fake", "geometry"])

        return df_locations[["location_id", "commune_id", "fake", "geometry"]]