# FlandersEqasim
This repository contains the code to create an open data synthetic population of Flanders (including Brussels). It can also be adapted for other regions in Belgium (Wallonia or more specific regions like Antwerp). This project is an adaptation of the [Eqasim application](https://github.com/eqasim-org/ile-de-france) build by S. Hörl and M. Balac. 

## General
This project has as purpose to create an open data synthetic population of Flanders and Brussels. It takes as input several open data sources to create a data set which represents the population in that region. How to get these sources for the case study of Belgium is described in [a separate document](docs/data.md). This population includes the socio-demographic attributes of persons and households in the region, as well as their daily mobility patterns. Those consist of activities which are performed at certain locations (like work, education, shopping, ...) and which are connected by trips with a certain mode of transport.

Such a synthetic population is useful for many research and planning applications. Among others it can serve as an input to agent-based transport simulations, which simulate the daily mobility behaviour of people on a spatially and temporally detailed scale. For this purposes the start of a framework is given for the application MATSim, which is an agent- and activity-based transport simulation framework. However at this moment this is not yet fully tested as the focus lays on generating a general synthetic population

## How to run the existing code

To use the code, you have to clone the repository with `git`:
```bash
git clone https://github.com/LaraDeVlieger/FlandersEqasim.git
```
After downloading the repository, the first thing to do is set up a new environment with the correct version of each package. A separate environment is recommended especially for the use of the [synpp](https://github.com/eqasim-org/synpp) package. The full list can be found in [this document](requirements.txt). 

The next important file is `config.yml`, which is the configuration of the pipeline code.
For the pipeline to work, it is important to adjust two configuration values inside of `config.yml`:

- `working_directory`: This should be an *existing* (ideally empty) folder where the pipeline will put temporary and cached files during runtime. This will have the form of the path towards the location where your project is stored and then `\cache`
- `data_path`: This should be the path to the folder where you were collecting and arranging all the raw data sets. In the proposed case study this will be the location where your project is stored and then `\data`
- `output_path`: This should be the path to the folder where the output data of the pipeline should be stored. It must exist and should ideally be empty for now. It takes the same form as the `working_directory`. 

An easy way to set up the working/output directory, is shown below. These are already configured in `config.yml`:

```bash
mkdir cache
mkdir output
```

The way `config.yml` is configured it will create the relevant output files in the `output` folder.

Next all of the data sources need to be implemented and prepared. Most of those for the current case study are already included, however some are too big for an online repository. These can be downloaded directly from the source or can be provided additionally by the authors in a zipped folder. More about this is provided in [the document about the data](docs/data.md). 

The next step is to run the pipeline, call the [synpp](https://github.com/eqasim-org/synpp) runner:

```bash
python3 -m synpp
```

It will automatically detect the `config.yml`, process all the pipeline code and eventually create the synthetic population. You should see a couple of intermediate messages from several stages running one after another. These give the user an idea what the pipeline is actually doing. 

After running, you should be able to see a couple of files in the `output` folder:

- `meta.json` contains some meta data, e.g. with which random seed or sampling
rate the population was created and when.
- `persons.csv` and `households.csv` contain all persons and households in the
population with their respective sociodemographic attributes.
- `activities.csv` and `trips.csv` contain all activities and trips in the
daily mobility patterns of these people including attributes on the purposes
of activities or transport modes for the trips.
- `activities.gpkg` and `trips.gpkg` represent the same trips and
activities, but in the spatial *GPKG* format. Activities contain point
geometries to indicate where they happen and the trips file contains line
geometries to indicate origin and destination of each trip.


## Additional information
Exactly how the adaptation was performed from the Eqasim version for Île-de-France, to one for Flanders is described in the paper provided by the authors. Furthermore all of the exact changes are listed in a powerpoint. 


