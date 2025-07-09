import requests
import json
import sys

def get_exodataset(select_strs, table_name, where_dict):
    """
    Function makes a TAP request to NASA exoplanet database, pscomppar and provided SQL arguments.
    Retrieves data from that TAP request (partially formatted as an SQL query) as a JSON.
    :param select_strs: List of strings to place after "SELECT" SQL phrase in url string. Can involve
                        getting specific columns from NASA table.
    :param table_name: String name of NASA data table.
    :param where_dict: Dictionary of table definitions (keys) and their name/numeric values shown as strings (values).
                       Used to find exoplanets based on "AND" inclusions only.
    :return: JSON response
    """

    # Set the API URL
    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=SELECT+"
    select_string = ",+".join(select_strs)
    from_string = "FROM+" + table_name + "+"
    where_string = "WHERE+"
    for key in where_dict:
        where_string += key + "=" + where_dict[key] + "+and+"
    where_string = where_string.removesuffix("+and+")

    query_string = url + "query=" + select_string + from_string + where_string + "&format=json"
    print(query_string)

    # Set the headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    # Send the request
    # NOTE: Bug here - Response Status code 400.
    response = requests.get(url, headers=headers)
    print("Finished getting request")
    print(response)
    return response

def calc_escape_velocity(response):
    """
    Calculates each exoplanet's escape velocity within the JSON response using the exoplanet's radius
    in Earth radius units and the exoplanet's mass in Earth mass units.

    :param response: JSON containing exoplanet data derived from SQL query on NASA datatable. Has columns such as
                     'pl_radj' and 'pl_bmassj'
    :return: Dictionary of exoplanet names (keys) and their escape velocities (values)
    """
    # Check the response status code
    if response.status_code == 200:
        # Decode the response
        data = response.json()

        # Get the results
        results = data["results"]
        # results = data

        # Create a list to store the planet data
        planet_data = []

        # Loop through the results
        for i in range(min(len(results), 10)):
            # Get the planet data
            planet = results[i]

            # Get the radius and mass of the planet
            radius = planet["pl_radj"]
            mass = planet["pl_bmassj"]

            # Append the data to the list
            planet_data.append([radius, mass])

        # Print the planet data
        print(planet_data)
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    # Provide the strings needed to create a SQL query on a NASA database
    select_args = ["TOP 20", "pl_radj", "pl_bmassj"]
    nasa_table = "pscomppars"
    where_args = {"sy_pnum": "1",
                  "pl_ntranspec": "2"}

    # Get dataset and calculate escape velocities with dataset
    output_response = get_exodataset(select_args, nasa_table, where_args)
    calc_escape_velocity(output_response)