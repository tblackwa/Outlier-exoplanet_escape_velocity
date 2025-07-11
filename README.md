# Outlier-exoplanet_escape_velocity
This project functions as inspiration for writing coding prompts in Outlier data annotation work. 

## Project Goal
- To gather any or some specific exoplanets based on various exoplanet features (number of moons, planets in system, temp, etc.) 
  and their corresponding data (exoplanet's radius and exoplanet's mass)to calculate each exoplanet's escape velocity.
- To gather this data, the code will use the TAP service to interact with NASA's Exoplanet Archive (https://exoplanetarchive.ipac.caltech.edu/)
  by making browser requests or PyVO TAP requests to that API.

### Additional Details
- Performing a TAP service call involves using the NASA Exoplanet Archive TAP endpoint (https://exoplanetarchive.ipac.caltech.edu/TAP)
  and then performing an ADQL query with that TAP endpoint.
- This ADQL query accesses various tables in the NASA Exoplanet Archive, such as the Composite Planet Data table (i.e., "pscomppars"),
  Confirmed Planets table (i.e., "ps"), etc.
- This project uses the Composite Planet Data table to get more data on various features of exoplanets. However, the code is flexible
  enough to run queries on different tables.
- Check https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html to get more information on how to create TAP queries
  with only `requests` or with `pyvo`. The link also has further defintions on each table in the exoplanet archive database.

### Installation Details
To run the code within the project, the provided packages must be installed:
1. requests
2. pyvo
3. astropy
4. pillow
5. defusedxml

Execute this installation command in your cmd window:

```bash
pip install requests pyvo astropy pillow defusedxml
```
