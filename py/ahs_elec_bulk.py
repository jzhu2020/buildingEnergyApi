# Copyright 2018 BACnet Gateway.  All rights reserved.

try:
    import time
    import argparse
    import pandas as pd
    from bacnet_gateway_requests import get_bulk

    start_time = time.time()

    # Get hostname and port of BACnet Gateway
    parser = argparse.ArgumentParser( description='Test BACnet Gateway', add_help=False )
    parser.add_argument( '-h', dest='hostname' )
    parser.add_argument( '-p', dest='port' )
    args = parser.parse_args()

    # Read spreadsheet into a dataframe.
    # Each row contains the following:
    #   - Label
    #   - Facility
    #   - Instance ID of electric meter
    df = pd.read_csv( '../csv/ahs_elec.csv' )

    # Initialize empty bulk request
    bulk_rq = []

    # Iterate over the rows of the dataframe, adding elements to the bulk request
    for index, row in df.iterrows():

        # Append facility/instance pairs to bulk request
        bulk_rq.append( { 'facility': row['Facility'], 'instance': row['Meter'] } )

    # Issue get-bulk request
    bulk_rsp = get_bulk( bulk_rq, args.hostname, args.port )

    # Extract map from get-bulk response
    map = bulk_rsp['rsp_map']

    # Output column headings
    print( 'Feeder,Meter,Units' )

    # Iterate over the rows of the dataframe, displaying meter readings extracted from map
    for index, row in df.iterrows():

        # Initialize empty display values
        value = ''
        units = ''

        # Get facility of current row
        facility = row['Facility']

        # Try to extract current row's meter reading from map
        if facility in map:

            instance = str( row['Meter'] )
            if instance and ( instance in map[facility] ):
                rsp = map[facility][instance]
                property = rsp['property']
                value = int( rsp[property] ) if rsp[property] else ''
                units = rsp['units']

        # Output CSV format
        print( '{0},{1},{2}'.format( row['Label'], value, units ) )

    # Report elapsed time
    elapsed_time = round( ( time.time() - start_time ) * 1000 ) / 1000
    print( '\nElapsed time: {0} seconds'.format( elapsed_time ) )


except KeyboardInterrupt:
    print( 'Bye' )
    import sys
    sys.exit()