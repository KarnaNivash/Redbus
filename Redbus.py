import streamlit as st
import pyodbc
import pandas as pd

# SQL Connection Function
def get_routes_and_seat_types_from_sql(state):
    try:
        # Connect to SQL Server
        connection = pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost\SQLEXPRESS;"
            "Database=BusDetails;"
            "UID=sa;"
            "PWD=123;"
        )
        cursor = connection.cursor()
        
        # Query to fetch distinct states
        state_query = "SELECT DISTINCT State_name FROM RedBus_BusDetails"
        cursor.execute(state_query)
        states = [row[0] for row in cursor.fetchall()]

        # Initialize data for routes and seat types
        routes = []
        seat_types = [] 
        Star_Rating = []
        Departing_Time = []
        price = []

        if state:
            # Fetch routes for the selected state
            routes_query = "SELECT DISTINCT Route_Name FROM RedBus_BusDetails WHERE State_name = ? ORDER BY 1 DESC"
            cursor.execute(routes_query, (state,))
            routes = [row[0] for row in cursor.fetchall()]

            # Fetch seat types for the selected state
            seat_types_query = "SELECT DISTINCT Bus_type FROM RedBus_BusDetails WHERE State_Name=? ORDER BY 1 DESC"
            cursor.execute(seat_types_query, (state,))
            seat_types = [row[0] for row in cursor.fetchall()]

        cursor.close()
        connection.close()
        return states, routes, seat_types, Star_Rating, Departing_Time, price

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return [], [], [], [], [], []

# Fetch detailed bus information based on filters
def get_bus_details(state, route, seat_type, Star_Rating, Departing_Time, price):
    try:
        # Connect to SQL Server
        connection = pyodbc.connect(
            "Driver={ODBC Driver 17 for SQL Server};"
            "Server=localhost\SQLEXPRESS;"
            "Database=BusDetails;"
            "UID=sa;"
            "PWD=123;"
        )
        cursor = connection.cursor()

        query = """
        SELECT Route_Name, Bus_type, State_name, Departing_Time, Reaching_Time, Price, Star_Rating, Seat_Availability, Duration
        FROM RedBus_BusDetails
        WHERE State_name = ?
        """
        
        params = [state]

        # Add route filter
        if route != "Select":
            query += " AND Route_Name = ?"
            params.append(route)

        if seat_type != "Select":
            if seat_type == "Seater A/C":
                query += " AND Bus_type like '%Seater%' and Bus_type like '%A/C%' and Bus_type not like '%Non%'"
            elif seat_type == "Seater Non A/c":
                query += " AND Bus_type like '%Seater%' and Bus_type like '%Non%'"
            elif seat_type == "Sleeper A/c":
                query += " AND Bus_type like '%Sleeper%' and Bus_type like '%A/C%' and Bus_type not like '%Non%'"
            elif seat_type == "Sleeper Non A/c":
                query += " AND Bus_type like '%Sleeper%' and Bus_type like '%Non%'"

        # Add star rating filter based on ranges    
        if Star_Rating != "Select":
            if float(Star_Rating) <= 2:
                query += " AND Star_Rating BETWEEN 1.1 AND 2.0"
            elif float(Star_Rating) <= 3:
                query += " AND Star_Rating BETWEEN 2.1 AND 3.0"
            elif float(Star_Rating) <= 4:
                query += " AND Star_Rating BETWEEN 3.1 AND 4.0"
            elif float(Star_Rating) <= 5:
                query += " AND Star_Rating BETWEEN 4.1 AND 5.0"

        # Add departing time
        if Departing_Time != "Select":
            if Departing_Time == '00:00 - 12:00':
                query += " AND Departing_Time BETWEEN '00:00' AND '12:00'"
            elif Departing_Time == '12:01 - 23:59':
                query += " AND Departing_Time BETWEEN '12:01' AND '23:59'"

        # Add price filter
        if price != "Select":
            if price == '1000':
                query += " AND Price BETWEEN 0 AND 1000"
            elif price == '2000':
                query += " AND Price BETWEEN 1001 AND 2000"
            elif price == '3000':
                query += " AND Price BETWEEN 2001 AND 3000"

        # Execute query
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()

        # Process the data to convert the raw string to a tuple
        parsed_data = []
        for row in data:
            route_name = row[0]
            bus_type = row[1]
            state_name = row[2]
            departing_time = row[3]
            Reaching_Time = row[4]
            price = row[5]
            star_rating = row[6]
            seat_availability = row[7]
            Duration = row[8]
            parsed_data.append([route_name, bus_type, state_name, departing_time,Reaching_Time, price, star_rating, seat_availability, Duration])

        # Convert processed data into DataFrame
        columns = ['Route Name', 'Bus Type', 'State', 'Start Time', 'Reaching Time' ,'Price', 'Star Rating', 'Seat Availability', 'Duration']
        df = pd.DataFrame(parsed_data, columns=columns)


        cursor.close()
        connection.close()
        return df

    except Exception as e:
        st.error(f"Error fetching bus details: {e}")
        return pd.DataFrame()

# App Title
st.markdown('<h1 style="color:red; font-size:2.25em; font-weight:600; margin-bottom:0.8rem;">Red Bus</h1>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Main Menu")
option = st.sidebar.radio("Select an Option:", ["Home Page", "Booking"])

# Home Page
if option == "Home Page":
    st.title("Welcome to Home Page")
    st.write(
        """
        **RedBus** is an online bus ticket booking company that provides easy and secure 
        bus ticket booking through its website and mobile apps for iOS and Android. 
        Explore routes and plan your travel effortlessly.
        """
    )

# Booking Page
elif option == "Booking":
    st.title("Book Tickets")
   
    # Fetch available states and related data
    with st.spinner('Fetching data...'):
        states, routes, seat_types, Star_Rating, Departing_Time, price = get_routes_and_seat_types_from_sql(None)
    state = st.selectbox('State:', ['Select'] + states)

    if state != "Select":
        with st.spinner('Loading routes and seat types...'):
            _, routes, seat_types, _, _, _ = get_routes_and_seat_types_from_sql(state)

        if routes:
            col1, col2 = st.columns(2)

            with col1:
                route = st.selectbox('Route:', ['Select'] + routes)

            with col2:
                seat_type = st.selectbox('Seat Type:', ['Select', 'Seater A/C', 'Seater Non A/C', 'Sleeper A/C', 'Sleeper  Non A/C'])

            col3, col4 = st.columns(2)

            with col3:
                Star_Rating = st.selectbox('Star_Rating (1 to 5):', ['Select', '1', '2', '3', '4', '5'])

            with col4:
                Departing_Time = st.selectbox(
                    'Bus Starting Time:',
                    ['Select', '00:00 - 12:00', '12:01 - 23:59']
                )

            price = st.selectbox('Price (Below):', ['Select', '1000', '2000', '3000'])

            # Search Button
            if st.button('Search'):
                # Fetch bus details based on selected filters
                with st.spinner('Fetching bus details...'):
                    bus_details_df = get_bus_details(state, route, seat_type, Star_Rating, Departing_Time, price)
                    
                    if not bus_details_df.empty:
                        st.dataframe(bus_details_df)
                    else:
                        st.warning("No buses found for the selected filters.")
        else:
            st.error(f"No routes available for {state}.")
    else:
        st.write("Please select a state to view the available routes and seat types.")


