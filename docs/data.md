## Gathering the data

To create the scenario, a couple of data sources must be collected. It is best to start with an separate folder, e.g. `/data`. All data sets need to be named in a specific way and put into specific sub-directories. The following paragraphs describe this process. 

If the current project is downloaded certain files are already included in this case only 1, 2, 3 need to be implemented either from the source directly or from an additionally provided folder. 
However if the process should be adapted outside of Belgium other sources should be used for each of the following steps. In that case it is possible to start from this project or from the original one for [Île-de-France](https://github.com/eqasim-org/ile-de-france). 
For specific zones within Belgium adaptations can be made within this project, more is explained in section: [other cases in Belgium](#section-adapt). 

### 1) Census data (RP 2019)

Census data containing the socio-demographic information of people living in Belgium is available from statbel:

- [Census data](https://statbel.fgov.be/nl/open-data?category=189&page=1)
- Here all of the files are given in parts, each with separate characteristics for the current cases the following numbers need to be downloaded: `TF_CENSUS_2011_HC07_L.xlsx`, `TF_CENSUS_2011_HC10_L.xlsx`, `TF_CENSUS_2011_HC24_L.xlsx`, `TF_CENSUS_2011_HC56_L.xlsx`. 
- These need to be combined into one big data set, there are several ways to do so, one is implemented in the folder ???? or in separate zip????
- For the current code to work this needs to be saved under the name `census_2011\dataset_enriched.csv` in the data folder

### 2) Spatial data (zonal_data)


### 3) Poidpy (poidpy)


### 4) Population totals


### 5) Origin-destination data


### 6) Income tax data
The tax data set is available from statbel:

- [Income tax data](https://statbel.fgov.be/en/open-data/fiscal-statistics-income)
- Download the data in **xlsx** format
- For the current code to work this needs to be saved under the name `incomeBE20\fisc2020_D_NL.xls` in the data folder

### 7) National household travel survey (ENTD 2008)

As the Belgian department doesn't have this publicly available the French data set is used.
The national household travel survey is available from the Ministry of Ecology:

- [National household travel survey](https://www.statistiques.developpement-durable.gouv.fr/enquete-nationale-transports-et-deplacements-entd-2008)
- Scroll all the way down the website to the **Table des donnés** (a clickable
pop-down menu).
- You can either download all the available *csv* files in the list, but only
a few are actually relevant for the pipeline. Those are:
  - Données socio-démographiques des ménages (Q_tcm_menage_0.csv)
  - Données socio-démographiques des individus (Q_tcm_individu.csv)
  - Logement, stationnement, véhicules à disposition des ménages (Q_menage.csv)
  - Données trajets domicile-travail, domicile-étude, accidents (Q_individu.csv)
  - Données mobilité contrainte, trajets vers lieu de travail (Q_ind_lieu_teg.csv)
  - Données mobilité déplacements locaux (K_deploc.csv)
- Put the downloaded *csv* files in to the folder `data/entd_2008`.


## <a name="section-adapt"></a>Adaptations within Belgium

Most of the data sources are provided for the whole of Belgium, this means that filtering out the data can result in specific populations for certain regions. 
There are two main sources which lay on the basis of this information, the census and the information from poidpy. For poidpy it is ....
As most of the merging is done on the basis of the census data it is very important to define the requested zones in this part. At the moment here only the zones for Flanders and Brussels are selected, however it is very easy to filter out more zones. The filtering is now done on the level of the provinces in the file ´data\census\filtered.py´, so choosing a region on this level is the easiest as it means just giving a different code as parameter. However the code in this file can also be adapted for a more precise level of zones. 
