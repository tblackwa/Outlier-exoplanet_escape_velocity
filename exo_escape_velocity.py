import numpy as np
import requests
import pyvo as vo
import sys

def get_vo_exodataset(ADQL_query):
    """
    PyVO implementation to access NASA Exoplanet Archive tables with TAP. Involves connecting
    to the NASA TAP endpoint with PyVO, and then provide the ADQL query as an arg. Simplifies
    much of the fetching and produces a DALTable rather than a JSON response.

    :param ADQL_query: The ADQL query used to access specific areas of data within the Exoplanet Archive database.
    :return: An astropy table consisting of the exoplanet's and their data fetched from the ADQL query.
    """
    # Make TAP query
    nasa_tap_url = "https://exoplanetarchive.ipac.caltech.edu/TAP"
    tap_service = vo.dal.TAPService(nasa_tap_url)

    # Change DALtable from query to astropy table
    result = tap_service.search(ADQL_query)
    astro_table = result.to_table()

    # TODO: Clean rows and columns for any masked values/columns

    return astro_table

def get_exodataset(select_strs, table_name, where_dict, select_specified_rows=0):
    """
    Function makes a TAP request to NASA exoplanet database, pscomppar and provided SQL arguments.
    Retrieves data from that TAP request (partially formatted as an SQL query) as a JSON.
    :param select_strs: List of strings to place after "SELECT" SQL phrase in url string. Can involve
                        getting specific columns from NASA table.
    :param table_name: String name of NASA data table.
    :param where_dict: Dictionary of table definitions (keys) and their name/numeric values shown as strings (values).
                       Used to find exoplanets based on "AND" inclusions only.
    :param select_specified_rows: Number of rows to get data from the top of the specified table. If default is
                                  provided (0), all rows will be acquired.
    :return: JSON response
    """

    # Set the API URL
    base_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query="

    # If not default value, select the top number of rows specified with
    # the columns from the provided 'select_strs' list
    if select_specified_rows != 0:
        select_string = "select+top+" + str(select_specified_rows) + "+" + ",+".join(select_strs) + "+"

    # If default value is specified, select only the columns from the provided 'select_strs' list
    else:
        select_string = "select+" + ",+".join(select_strs) + "+"

    # Create FROM phrase of SQL query
    from_string = "from+" + table_name + "+"

    # Create WHERE phrase of SQL query
    where_string = "where+" + ""
    for key in where_dict:
        where_string += key + "=" + where_dict[key] + "+and+"
    where_string = where_string.removesuffix("+and+")

    url = base_url + select_string + from_string + where_string + "&format=json"
    print(url)

    # Set the headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    # Send the request
    response = requests.get(url, headers=headers)
    results = None
    print("Finished getting request")


    # Handle response status code
    if response.status_code == 200:
        # Get results from the response
        results = response.json()
    else:
        print(f"Error: {response.status_code}")
        sys.exit(1)

    #TODO: Overall, clean JSON exoplanet data of any missing values/NaN
    #TODO: I.e., Remove specific exoplanet data (rows/keys) from JSON once missing values are detected

    return results

def calc_escape_velocity(results, earth_units_flag=True):
    """
    Calculates each exoplanet's escape velocity with the provided JSON/astropy table using the exoplanet's radius
    in Earth radius units and the exoplanet's mass in Earth mass units. The results will have at least key entries
    'pl_name', 'pl_rade', 'pl_bmasse', 'pl_radj', and 'pl_bmassj'. Here's the description of these keys:

    - 'pl_name': Exoplanet name
    - 'pl_rade': Exoplanet's radius in units of Earth's radius
    - 'pl_bmasse': Exoplanet's mass in units of Earth's mass
    - 'pl_radj': Exoplanet's radius in units of Jupiter's radius
    - 'pl_bmassj': Exoplanet's mass in units of Jupiter's mass

    :param results: JSON or astropy table containing exoplanet data derived from SQL query on NASA datatable.
                    Has keys such as 'pl_radj' and 'pl_bmassj'.
    :param earth_units_flag: Bool used to calculate which conversion variable to use for exoplanet's radius and mass.
                             If true, convert the radius and mass from Earth's mass and radius units,
                             else, convert the radius and mass from Jupiter's mass and radius units.
    :return: 2D List of exoplanet names and their escape velocities.
    """

    # Define the constants needed for escape velocity computation
    earth_mass = 5.97219 * 10 ** 24
    earth_radius = 6.371 * 10 ** 6
    jupiter_mass = 1.89813 * 10 ** 27
    jupiter_radius = 6.9911 * 10 ** 7
    g = 6.674 * 10 ** -11

    planet_data = []
    for i in range(len(results)):
        # Get the planet data
        planet = results[i]

        # Get the radius and mass of the planet and convert them with Earth or Jupiter units
        if earth_units_flag:
            mass = planet["pl_bmasse"] * earth_mass
            radius = planet["pl_rade"] * earth_radius
        else:
            mass = planet["pl_bmassj"] * jupiter_mass
            radius = planet["pl_radj"] * jupiter_radius

        # Calculate escape velocity and change units from m/s to km/s
        escape_velocity = (2*g*mass/radius) ** (1/2)
        escape_velocity /= 1000

        # Type check velocity is a np.float
        # If not, update to a np.float to maintain consistency between requests and PyVO methods
        if not isinstance(escape_velocity, np.floating):
            escape_velocity = np.float64(escape_velocity)

        planet_data.append([planet["pl_name"], escape_velocity])

    print(planet_data)

if __name__ == "__main__":
    # Provide the strings needed to create a ADQL query on a NASA database for requests method
    select_args = ["pl_name", "pl_rade", "pl_radj", "pl_bmasse", "pl_bmassj"]
    nasa_table = "pscomppars"
    where_args = {"sy_pnum": "1",
                  "pl_ntranspec": "2"}

    # Provide ADQL query for pyvo method
    query = "SELECT TOP 5 pl_name, pl_rade, pl_bmasse FROM pscomppars WHERE sy_pnum=1 AND pl_ntranspec=2"

    # True = use pyvo method, False = use requests method
    use_pyvo = False

    if use_pyvo is True:
        exo_table = get_vo_exodataset(query)
        calc_escape_velocity(exo_table, earth_units_flag=True)
    else:
        json_results = get_exodataset(select_args, nasa_table, where_args, select_specified_rows=5)
        calc_escape_velocity(json_results, earth_units_flag=True)
