
import csv
import datetime
import tkinter as tk
from tkinter import ttk
import Truck
from HashTable import GenerateHashMap
from Package import Package

address_updated = False  # flag for updating mileage if route is updated


def read_csv_file(filepath):
    """
    Reads the content of a CSV file and returns it as a list of rows.
    """
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)


def populate_package_data(filename, package_hash_table):
    """
    Reads package data from a CSV file, creates Package objects, and inserts them into the provided hash table.
    """
    try:
        with open(filename) as package_info:
            p_data = csv.reader(package_info)
            for row in p_data:
                [package_id, package_address, package_city, package_state, package_zipcode, package_deadline,
                 package_weight, *_] = row
                package_id = int(package_id)
                package_status = "At the Hub"

                # Create a Package object
                package = Package(package_id, package_address, package_city, package_state, package_zipcode,
                                  package_deadline, package_weight, package_status)

                # Insert the package into the hash table
                package_hash_table.insert(package_id, package)
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")


def distance_to_delivery(start, destination):
    """
    Retrieves the distance between the start and destination addresses.
    """
    distance = distance_data[start][destination]
    if distance == '':
        distance = distance_data[destination][start]

    return float(distance)


def distance_to_home(start):
    """
    Retrieves the distance between the address and the hub(index 0).
    """
    start = int(start)
    return float(distance_data[start][0] or distance_data[0][start])


def extract_address(address):
    """
    Searches for the provided address in the address_data list and returns the corresponding address ID.
    """
    address_column_index = 2
    id_column_index = 0

    for row in address_data:
        if address in row[address_column_index]:
            return int(row[id_column_index])


def create_truck(packages, depart_time):
    """
    Creates and returns a new Truck object with predefined parameters.
    """
    return Truck.Truck(16, 18, packages, 0.0, "4001 South 700 East", depart_time)


def route_packages(truck, p_table):
    """
    Determines the route for the given truck to deliver its packages based on the nearest-neighbor strategy.
    Once all packages are delivered, the truck returns to the hub.
    """
    not_delivered = [p_table.lookup(packageID) for packageID in truck.packages]
    truck.packages.clear()

    # Deliver packages using nearest neighbor
    # Start a loop as long as there are packages that have not been delivered.
    while not_delivered:
        shortest_distance = float('inf')  # Set the initial shortest distance to infinity.
        closest_package = None  # Initialize a variable to hold the closest package.

        for package in not_delivered:  # Iterate through each package that hasn't been delivered.
            # Calculate the distance from the current location of the truck to the delivery address of package.
            current_distance = distance_to_delivery(extract_address(truck.address), extract_address(package.address))
            if current_distance < shortest_distance:  # Check if the distance to the current package is less than the shortest distance found
                shortest_distance = current_distance  # If it is, update the shortest distance to the current distance.
                closest_package = package  # Update the closest package to the current package.

        truck.packages.append(closest_package.id)  # Add the ID of the closest package to the truck's package list.
        not_delivered.remove(
            closest_package)  # Remove the closest package from the list of packages that have not been delivered.

        # Update truck's attributes
        if truck.time < truck.depart_time:
            truck.time = truck.depart_time
        truck.mileage += shortest_distance
        truck.address = closest_package.address
        truck.time += datetime.timedelta(hours=shortest_distance / 18)

        # Update the delivered package's attributes
        closest_package.delivery_time = truck.time
        closest_package.departure_time = truck.depart_time

    # Return the truck to the hub after all packages are delivered
    distance_home = distance_to_home(extract_address(truck.address))
    truck.mileage += distance_home
    truck.time += datetime.timedelta(hours=distance_home / 18)
    truck.address = "4001 South 700 East"  # Reset to hub address


def create_label_and_grid(package, row, col):
    """
    Helper function to create a label for the package and place it in the result frame.
    """
    label = ttk.Label(result_frame, text=str(package), wraplength=300, anchor='w', justify='left')
    label.grid(row=row, column=col, padx=10, pady=10, sticky='w')


def reroute_undelivered_packages(truck, p_table, user_selected_time):
    """
    Reroutes the undelivered packages on a truck after an address update.
    Assumes packages delivered before user_selected_time are already delivered and will not be rerouted.
    """
    # Filter out packages that were already delivered
    not_delivered = [p_table.lookup(packageID) for packageID in truck.packages if
                     p_table.lookup(packageID).delivery_time > user_selected_time]
    truck.packages = [pkg.id for pkg in not_delivered]
    # Reroute using algorithm from previous method
    while not_delivered:
        shortest_distance = float('inf')
        closest_package = None

        for package in not_delivered:
            current_distance = distance_to_delivery(extract_address(truck.address), extract_address(package.address))
            if current_distance < shortest_distance:
                shortest_distance = current_distance
                closest_package = package

        truck.packages.append(closest_package.id)
        not_delivered.remove(closest_package)

        # Update truck's attributes
        if truck.time < truck.depart_time:
            truck.time = truck.depart_time
        truck.mileage += shortest_distance
        truck.address = closest_package.address
        truck.time += datetime.timedelta(hours=shortest_distance / 18)

        # Update the delivered package's attributes
        closest_package.delivery_time = truck.time
        closest_package.departure_time = truck.depart_time

    # Return the truck to the hub after all packages are delivered
    distance_home = distance_to_home(extract_address(truck.address))
    truck.mileage += distance_home
    truck.time += datetime.timedelta(hours=distance_home / 18)
    truck.address = "4001 South 700 East"  # Reset to hub


def update_incorrect_address(user_selected_time):
    """
    Update the address of package #9 if the user-selected time is 10:20 a.m. or later.
    Then reroutes the undelivered packages on the same truck.
    """
    selected_hour = user_selected_time.seconds // 3600
    selected_minute = (user_selected_time.seconds // 60) % 60

    if (selected_hour > 10) or (selected_hour == 10 and selected_minute >= 20):
        global address_updated
        package_9 = package_table.lookup(9)
        if package_9 and not address_updated:
            package_9.address = "410 S State St"
            package_9.city = "Salt Lake City"
            package_9.state = "UT"
            package_9.zipcode = "84111"

            # Find the truck carrying package #9 and reroute the undelivered packages on it
            truck = find_truck_carrying_package(9)
            if truck:
                reroute_undelivered_packages(truck, package_table, user_selected_time)
                update_mileage_label()
                address_updated = True  # Flag locks total_mileage after address update


def check_package_status():
    """
    Updates and displays the package status based on user-selected time in the GUI.
    The status can be displayed for all packages or a specific selected package.
    """
    user_hour = hour_combo.get()
    user_minute = minute_combo.get()
    user_selected_time = datetime.timedelta(hours=int(user_hour), minutes=int(user_minute))
    update_incorrect_address(user_selected_time)
    selected_package_id = combo_packages.get()

    # Clear labels
    for label in result_frame.winfo_children():
        label.destroy()

    if selected_package_id == "All":
        row, col = 0, 0
        for packageID in range(1, 41):  # Assuming 40 packages
            current_package = package_table.lookup(packageID)
            current_package.update_status(user_selected_time)
            create_label_and_grid(current_package, row, col)

            col += 1
            if col > 7:  # 8 columns
                col = 0
                row += 1
    else:
        single_package = package_table.lookup(int(selected_package_id))
        single_package.update_status(user_selected_time)
        create_label_and_grid(single_package, 0, 0)


def find_truck_carrying_package(package_id):
    """
    Determine which truck is carrying the specified package.
    """
    if package_id in truck1.packages:
        return truck1
    elif package_id in truck2.packages:
        return truck2
    elif package_id in truck3.packages:
        return truck3
    else:
        return None


def update_mileage_label():
    """
    Updates mileage when a truck is rerouted
    """
    total_mileage = truck1.mileage + truck2.mileage + truck3.mileage
    mileage_label.config(text=f"Total mileage for the route is {total_mileage} miles")


def initialize_gui():
    """
    Initializes and sets up the main GUI elements, layout, and styles.
    """
    global root, hour_combo, minute_combo, combo_packages, result_frame, mileage_label
    root = tk.Tk()

    root.title("Package Status")
    root.state('zoomed')  # Set window maximized

    # Create and display the mileage label
    mileage_label = ttk.Label(root, font=('Arial', 16))
    mileage_label.pack(pady=20)
    update_mileage_label()

    # Create a frame for time
    time_frame = ttk.Frame(root)
    time_frame.pack(pady=5)

    # Label for time
    time_label = ttk.Label(time_frame, text="Select Time:", font=('Arial', 14))
    time_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

    # Hours Combobox
    hours = [f"{i:02}" for i in range(24)]  # Hours, military time
    hour_combo = ttk.Combobox(time_frame, values=hours, font=('Arial', 14), width=3)
    hour_combo.set(hours[0])  # Set default value to 00
    hour_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    # Minutes Combobox
    minutes = [f"{i:02}" for i in range(0, 60, 5)]  # Minutes increment by 5
    minute_combo = ttk.Combobox(time_frame, values=minutes, font=('Arial', 14), width=3)
    minute_combo.set(minutes[0])  # Set default value to 00
    minute_combo.grid(row=0, column=2, padx=5, pady=5, sticky="w")

    # Packages Combobox
    combo_label = ttk.Label(root, text="Select a package:", font=('Arial', 14))
    combo_label.pack(pady=5)
    combo_packages = ttk.Combobox(root, values=["All"] + [str(i) for i in range(1, 41)],  # Assuming 40 packages
                                  font=('Arial', 14))
    combo_packages.set("All")  # Set default value
    combo_packages.pack(pady=5)

    # Check status button
    style = ttk.Style()
    style.configure("Custom.TButton", font=('Arial', 14))
    check_button = ttk.Button(root, text="Check Status", command=check_package_status, style="Custom.TButton")
    check_button.pack(pady=20)

    # Frame to hold package
    result_frame = ttk.Frame(root)
    result_frame.pack(pady=20, padx=20, fill='both', expand=True)

    # Configure columns to be centered and weighted equally
    for i in range(8):  # For 8 columns
        result_frame.columnconfigure(i, weight=1)

    root.mainloop()


def set_package_truck(truck, truck_number, package_table):
    """
    Assigns the truck number to each package carried by the truck.
    """
    for packageID in truck.packages:
        package = package_table.lookup(packageID)
        if package:
            package.truck = f"{truck_number}"


def main():
    """
    Entry point for the execution of the program. Sets up data, initializes objects,
    runs the core logic, and initializes the GUI.
    """
    global distance_data, address_data, truck1, truck2, truck3, package_table

    distance_data = read_csv_file("Resources/distance_table.csv")
    address_data = read_csv_file("Resources/address_table.csv")

    truck1 = create_truck([13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40], datetime.timedelta(hours=8))
    truck2 = create_truck([1, 3, 12, 17, 18, 21, 22, 23, 24, 26, 27, 35, 36, 38, 39], datetime.timedelta(hours=8))
    truck3 = create_truck([2, 4, 5, 6, 7, 8, 9, 10, 11, 25, 28, 32, 33], datetime.timedelta(hours=9, minutes=5))

    package_table = GenerateHashMap()
    populate_package_data("Resources/package_table.csv", package_table)

    set_package_truck(truck1, 1, package_table)
    set_package_truck(truck2, 2, package_table)
    set_package_truck(truck3, 3, package_table)

    route_packages(truck1, package_table)
    route_packages(truck2, package_table)
    truck3.depart_time = min(truck1.time, truck2.time)
    route_packages(truck3, package_table)

    initialize_gui()


if __name__ == "__main__":
    main()
