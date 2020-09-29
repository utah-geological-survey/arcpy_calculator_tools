import requests

def get_elev(x, units='Meters'):
    """Uses USGS elevation service to retrieve elevation
    :param x: longitude and latitude of point where elevation is desired
    :type x: list
    :param units: units for returned value; defaults to Meters; options are 'Meters' or 'Feet'
    :type units: str
    :returns: ned float elevation of location in meters
    :Example:
        >>> get_elev([-111.21,41.4])
        1951.99
    """ 
    
    values = {
        'x': x[0],
        'y': x[1],
        'units': units,
        'output': 'json'
    }

    elev_url = 'https://nationalmap.gov/epqs/pqs.php?'

    attempts = 0
    while attempts < 4:
         try:
             response = requests.get(elev_url, params=values).json()
             g = float(response['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation'])
             break
         except:
             print("Connection attempt {:} of 3 failed.".format(attempts))
             attempts += 1
             g = 0
    return g
def get_huc(x):
    """Receive the content of ``url``, parse it as JSON and return the object.
    :param x: [longitude, latitude]
    :returns: HUC12, HUC12_Name - 12 digit hydrologic unit code of location and the name associated with that code
    """
    values = {
        'geometry': '{:},{:}'.format(x[0], x[1]),
        'geometryType': 'esriGeometryPoint',
        'inSR': '4326',
        'spatialRel': 'esriSpatialRelIntersects',
        'returnGeometry': 'false',
        'outFields': 'huc12,name',
        'returnDistinctValues': 'true',
        'f': 'pjson'}

    huc_url = 'https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/6/query?'
    # huc_url = 'https://services.nationalmap.gov/arcgis/rest/services/USGSHydroNHDLarge/MapServer/10/query?'
    # huc_url2 = 'https://services.nationalmap.gov/arcgis/rest/services/nhd/mapserver/8/query?'
    response = requests.get(huc_url, params=values).json()
    return response['features'][0]['attributes']['huc12'], response['features'][0]['attributes']['name']

def get_fips(x):
    """Receive the content of ``url``, parse it as JSON and return the object.
    :param x: [longitude, latitude]
    :returns: tuple containing five digit county fips and county name
    """
    values = {'lat': '{:}'.format(x[1]), 'lon': '{:}'.format(x[0])}
    huc_url = "https://geo.fcc.gov/api/census/area?"
    response = requests.get(huc_url, params=values).json()
    return response['results'][0]['county_fips'][2:], response['results'][0]['county_name']

def USGSID(x):
    """Parses decimal latitude and longitude values into DDMMSSDDDMMSS01 USGS site id.
    See https://help.waterdata.usgs.gov/faq/sites/do-station-numbers-have-any-particular-meaning for documentation.
    :param x: [longitude,latitude]
    :type x: str
    :returns: USGS-style site id (groundwater) DDMMSSDDDMMSS01
    """
    return dms(x[1]) + dms(x[0]) + '01'

def dms(dec):
    """converts decimal degree coordinates to a usgs station id
    :param dec: latitude or longitude value in decimal degrees
    :return: usgs id value
    .. note:: https://help.waterdata.usgs.gov/faq/sites/do-station-numbers-have-any-particular-meaning
    """
    DD = str(int(abs(dec)))
    MM = str(int((abs(dec) - int(DD)) * 60)).zfill(2)
    SS = str(int(round((((abs(dec) - int(DD)) * 60) - int(MM)) * 60, 0))).zfill(2)
    if SS == '60':
        MM = str(int(MM) + 1)
        SS = '00'
    if MM == '60':
        DD = str(int(DD) + 1)
        MM = '00'
    return DD + MM + SS
