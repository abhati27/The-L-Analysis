import sqlite3
import matplotlib.pyplot as plt
import re


##################################################################
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()
    print("General stats:")

    # No. of Stations
    dbCursor.execute("SELECT COUNT(*) FROM Stations;")
    row = dbCursor.fetchone()
    num_stations = row[0]
    print(f"  # of stations: {num_stations:,}")
    
    # No. of Stops
    dbCursor.execute("SELECT COUNT(Stop_Name) FROM Stops;")
    row = dbCursor.fetchone()
    num_stops = row[0]
    print(f"  # of stops: {num_stops:,}")
    
    # No. of Ride Entries
    dbCursor.execute("SELECT COUNT(Station_ID) FROM Ridership;")
    row = dbCursor.fetchone()
    num_ride_entries = row[0]
    print(f"  # of ride entries: {num_ride_entries:,}")
    
    # Date Range
    dbCursor.execute("SELECT MIN(date(Ride_Date)), MAX(date(Ride_Date)) FROM Ridership;")
    row = dbCursor.fetchone()
    date_range_start, date_range_end = row
    print(f"  date range: {date_range_start} - {date_range_end}")
    
    # Total Ridership
    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership;")
    row = dbCursor.fetchone()
    total_ridership = int(row[0])
    print(f"  Total ridership: {total_ridership:,}")
    
    def print_ridership_summary(day_type, description):
        dbCursor.execute(f"SELECT SUM(Num_Riders) FROM Ridership WHERE Type_of_Day = '{day_type}';")
        row = dbCursor.fetchone()
        ridership = int(row[0])
        perc = float(round((ridership / total_ridership) * 100, 2))
        print(f"  {description} ridership: {ridership:,} ({perc:.2f}%)")
    
    # Weekday Ridership
    print_ridership_summary('W', 'Weekday')
    
    # Saturday Ridership
    print_ridership_summary('A', 'Saturday')
    
    # Sunday/Holiday Ridership
    print_ridership_summary('U', 'Sunday/holiday')
#####################################################################
# retrieve_stations()
# This function retrieves the stations that are “like” the user’s input
#
def retrieve_stations(dbConn):
    print()
    name = input("Enter partial station name (wildcards _ and %): ")
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC", [name])
    rows = dbCursor.fetchall()
    
    if len(rows) == 0:
        print("**No stations found...")  # No records found when fetched rows are 0
    else:
        for station_id, station_name in rows:
            print(f"{station_id} : {station_name}")
    
    return

#####################################################################
# output_ridership()
# This function retrieves and Outputs the ridership at each station, in ascending order by station name
#
def output_ridership(dbConn):
    total_riders = 0
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT Station_Name, SUM(Num_Riders) FROM Ridership a JOIN Stations b WHERE a.Station_ID = b.Station_ID GROUP BY Station_Name ORDER BY Station_Name ASC")
    rows = dbCursor.fetchall()

    if len(rows) == 0:
        print("**No stations found...")  # No records found when fetched rows are 0
        return

    print("** ridership all stations **\n")

    for station_name, num_riders in rows:
        total_riders += num_riders

    for station_name, num_riders in rows:
        perc_ridership = float(round((num_riders / total_riders) * 100, 2))
        print(f"{station_name}: {num_riders:,} ({perc_ridership:.2f}%)")



#####################################################################
# top_ten_busiest()
# This Function retrieves and Outputs the top-10 busiest stations in terms of ridership, in descending order by ridership
#
def top_ten_busiest(dbConn):
    dbCursor = dbConn.cursor()

    dbCursor.execute("SELECT Station_Name, SUM(Num_Riders) as ridersum FROM Ridership a JOIN Stations b WHERE a.Station_ID = b.Station_ID GROUP BY Station_Name ORDER BY ridersum DESC LIMIT 10;")
    rows = dbCursor.fetchall()

    if len(rows) == 0:  # No records found when fetched rows are 0
        print("**No stations found...")
        return

    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership;")
    total_riders = dbCursor.fetchone()[0]

    print("** top-10 stations **\n")

    for station_name, num_riders in rows:
        perc_ridership = float(round((num_riders / total_riders) * 100, 2))
        print(f"{station_name}: {num_riders:,} ({perc_ridership:.2f}%)")

####################################################################
# least_ten_busiest()
# This Function retrieves and Outputs the least-10 busiest stations in terms of ridership, in ascending order by ridership
#
def least_ten_busiest(dbConn):
    dbCursor = dbConn.cursor()

    dbCursor.execute("SELECT Station_Name, SUM(Num_Riders) as ridersum FROM Ridership a JOIN Stations b WHERE a.Station_ID = b.Station_ID GROUP BY Station_Name ORDER BY ridersum LIMIT 10;")
    rows = dbCursor.fetchall()

    if len(rows) == 0:  # No records found when fetched rows are 0
        print("**No stations found...")
        return

    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership;")
    total_riders = dbCursor.fetchone()[0]

    print("** least-10 stations **\n")

    for station_name, num_riders in rows:
        perc_ridership = float(round((num_riders / total_riders) * 100, 2))
        print(f"{station_name}: {num_riders:,} ({perc_ridership:.2f}%)")

####################################################################
# line_color_stops()
# This function takes a color from user as input, and outputs all stop names that are part of that line, in ascending order
#
def line_color_stops(dbConn):
    print("\n")
    user_color = input("Enter a line color (e.g. Red or Yellow): ")
    dbCursor = dbConn.cursor()

    dbCursor.execute("SELECT stop_name, direction, ada FROM stops s JOIN stopdetails sd ON s.stop_id = sd.stop_id JOIN lines l ON sd.line_id = l.line_id WHERE l.color = ? COLLATE NOCASE GROUP BY stop_name ORDER BY stop_name;", [user_color])
    rows = dbCursor.fetchall()

    if len(rows) == 0:  # No records found when fetched rows are 0
        print("**No such line...\n")
        return

    for stop_name, direction, ada_accessible in rows:
        accessibility = "yes" if ada_accessible == 1 else "no"
        print(f"{stop_name}: direction = {direction} (accessible? {accessibility})")

####################################################################
# ridership_by_month()
# This Function Outputs total ridership by month, in ascending order by month
#
def ridership_by_month(dbConn):
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT strftime('%m', Ride_Date), SUM(Num_Riders) FROM Ridership GROUP BY strftime('%m', Ride_Date) ORDER BY strftime('%m', Ride_Date) ASC;")
    print("** ridership by month **\n")
    rows = dbCursor.fetchall()

    for month, num_riders in rows:
        print(f"{month}: {num_riders:,}")

    user_choice = input("Plot? (y/n)")

    if user_choice.lower() == 'y':
        x = []
        y = []

        for row in rows:
            x.append(row[0])
            y.append(row[1])

        # plot labels and titles
        plt.xlabel("month")
        plt.ylabel("number of riders (x * 10^8)")
        plt.title("monthly ridership")
        plt.plot(x, y)
        plt.show()
    else:
        return
####################################################################
# ridership_by_year()
# This function Outputs total ridership by year, in ascending order by year
#
def ridership_by_year(dbConn):
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT strftime('%Y', Ride_Date), SUM(Num_Riders) FROM Ridership GROUP BY strftime('%Y', Ride_Date) ORDER BY strftime('%Y', Ride_Date) ASC;")
    rows = dbCursor.fetchall()
    print("** ridership by year **\n")

    for year, num_riders in rows:
        print(f"{year}: {num_riders:,}")

    user_choice = input("Plot? (y/n)")

    if user_choice.lower() == 'y':
        x = []
        y = []

        for row in rows:
            year_val = str(row[0])
            x.append(year_val[-2:])  # Extracting last 2 digits of Year for the plot's x axis
            y.append(row[1])

        plt.xlabel("year")
        plt.ylabel("number of riders (x * 10^8)")
        plt.title("yearly ridership")
        plt.plot(x, y)
        plt.show()
    else:
        return
####################################################################
# compare_ridership()
# This function takes user's Input for a year and the names of two stations (full or partial names), and then outputs the daily ridership at each station for that year (first and last 5 days)
#
def compare_ridership(dbConn):
    print()
    user_year = input("Year to compare against? ")
    print()
    user_station1 = input("Enter station 1 (wildcards _ and %): ")

    station_check_flag1 = dbConn.cursor()
    station_check_flag1.execute("SELECT COUNT(*) FROM Stations WHERE Station_Name LIKE ?;", [user_station1])
    check_rows1 = station_check_flag1.fetchall()
    total_stations1 = check_rows1[0][0]

    if total_stations1 < 1:
        print("**No station found...\n")
        return
    elif total_stations1 > 1:
        print("**Multiple stations found...\n")
        return
    else:
        db_cursor1 = dbConn.cursor()
        db_cursor1.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ?;", [user_station1])
        my_rows1 = db_cursor1.fetchall()
        print()
        user_station2 = input("Enter station 2 (wildcards _ and %): ")
        station_check_flag2 = dbConn.cursor()
        station_check_flag2.execute("SELECT COUNT(*) FROM Stations WHERE Station_Name LIKE ?;", [user_station2])
        check_rows2 = station_check_flag2.fetchall()
        total_stations2 = check_rows2[0][0]

        if total_stations2 < 1:
            print("**No station found...\n")
            return
        elif total_stations2 > 1:
            print("**Multiple stations found...\n")
            return
        else:
            db_cursor2 = dbConn.cursor()
            db_cursor2.execute("SELECT station_id, station_name FROM stations WHERE station_name LIKE ?;", [user_station2])
            my_rows2 = db_cursor2.fetchall()

            # Compare ridership and plot if requested
            compare_and_plot_ridership(dbConn, user_year, my_rows1, my_rows2)

def compare_and_plot_ridership(dbConn, user_year, station1_rows, station2_rows):
    print("Station 1:", station1_rows[0][0], station1_rows[0][1])
    station1_data = fetch_ridership_data(dbConn, station1_rows[0][1], user_year)
    display_ridership_data(station1_data)

    print("Station 2:", station2_rows[0][0], station2_rows[0][1])
    station2_data = fetch_ridership_data(dbConn, station2_rows[0][1], user_year)
    display_ridership_data(station2_data)

    user_choice = input("Plot? (y/n) ")

    if user_choice.lower() == 'y':
        plot_ridership_data(station1_rows[0][1], station1_data, station2_rows[0][1], station2_data, user_year)

def fetch_ridership_data(dbConn, station_name, user_year):
    cursor = dbConn.cursor()
    cursor.execute("SELECT r.Ride_Date, r.Num_Riders FROM Ridership r, Stations s WHERE r.station_id = s.station_id AND s.station_name = ? AND strftime('%Y', r.Ride_Date) = ? GROUP BY r.Ride_Date;", (station_name, user_year))
    return cursor.fetchall()

def display_ridership_data(ridership_data):
    date_data = [row[0].split()[0] for row in ridership_data]
    ridership = [row[1] for row in ridership_data]
    for i in range(5):
        print(date_data[i], ridership[i])
    for i in range(-5, 0):
        print(date_data[i],ridership[i])

def plot_ridership_data(station1_name, station1_data, station2_name, station2_data, user_year):
    day = list(range(0, len(station1_data)))
    ridership1 = [row[1] for row in station1_data]
    ridership2 = [row[1] for row in station2_data]
    
    plt.plot(day, ridership1, label=station1_name)
    plt.plot(day, ridership2, label=station2_name)
    plt.xlabel("day")
    plt.ylabel("number of riders")
    plt.title(f"Riders each day of {user_year}")
    plt.legend()
    plt.show()

####################################################################
# line_color_plot()
# This function takes user's Input for a line color and outputs all station names that are part of that line, in ascending order
#
def line_color_plot(dbConn):
    print()
    color = input("Enter a line color (e.g. Red or Yellow): ")

    dbCursor = dbConn.cursor()
    dbCursor.execute("""SELECT DISTINCT 
                            a.Station_Name, b.Latitude, b.Longitude 
                        FROM 
                            Stations as a 
                        JOIN 
                            Stops as b 
                        JOIN 
                            Stopdetails as sd 
                        JOIN 
                            Lines as l 
                        WHERE 
                            a.Station_ID = b.Station_ID 
                            AND b.Stop_ID = sd.Stop_ID 
                            AND sd.line_id = l.line_id 
                            AND l.color = ? COLLATE NOCASE 
                        GROUP BY 
                            a.station_name 
                        ORDER BY 
                            a.station_name;""",
                    (color,))
    rows = dbCursor.fetchall()

    if len(rows) == 0:  # No records found when rows fetched are 0
        print("**No such line...")
        return userCommandHelper(dbConn)

    stations = []
    latitudes = []
    longitudes = []

    for row in rows:
        print(f"{row[0]}: ({row[1]}, {row[2]})")
        stations.append(row[0])
        latitudes.append(row[1])
        longitudes.append(row[2])

    print()
    plot_choice = input("Plot? (y/n)")

    if plot_choice == 'y':
        image = plt.imread("chicago.png")
        xydims = [-87.9277, -87.5569, 41.7012, 42.0868]
        plt.imshow(image, extent=xydims)
        plt.title(color + " line")

        if color.lower() == "purple-express":
            color = "Purple"  # color="#800080"

        plt.plot(longitudes, latitudes, "o", c=color)

        for i, station in enumerate(stations):
            plt.annotate(station, (longitudes[i], latitudes[i]))

        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.show()

    else:
        return userCommandHelper(dbConn)

    return userCommandHelper(dbConn)
    

####################################################################
# userCommandHelper()
# This function calls the other functions to execute various SQL queries based on the user's command, including 'x' for exit.
#
def userCommandHelper(dbConn):
    while True:
        print("\nPlease enter a command (1-9, x to exit):")
        print(" 1: Retrieve Stations")
        print(" 2: Output Ridership")
        print(" 3: Top Ten Busiest")
        print(" 4: Least Ten Busiest")
        print(" 5: Line Color Stops")
        print(" 6: Ridership by Month")
        print(" 7: Ridership by Year")
        print(" 8: Compare Ridership")
        print(" 9: Line Color Plot")
        print(" x: Exit")
        userCommand = input().lower()

        if userCommand == '1':
            retrieve_stations(dbConn)
        elif userCommand == '2':
            output_ridership(dbConn)
        elif userCommand == '3':
            top_ten_busiest(dbConn)
        elif userCommand == '4':
            least_ten_busiest(dbConn)
        elif userCommand == '5':
            line_color_stops(dbConn)
        elif userCommand == '6':
            ridership_by_month(dbConn)
        elif userCommand == '7':
            ridership_by_year(dbConn)
        elif userCommand == '8':
            compare_ridership(dbConn)
        elif userCommand == '9':
            line_color_plot(dbConn)
        elif userCommand == 'x':
            break
        else:
            print("**Error, unknown command, try again...")



####################################################################
#
# main
#
print('** Welcome to CTA L analysis app **')
print()

database_name = input("Please enter the database name (e.g. chiTrains.db): ")

dbConn = sqlite3.connect(database_name)

print_stats(dbConn)

userCommandHelper(dbConn)

#
# done
#