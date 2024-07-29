# from ui import *             # Import all user interface functions

#
# Welcome!
#
# To analyze an image, follow the readMe directions for image preprocessing, then
# run this file to open the user interface. Select your file through the import button,
# and specify what kind of analysis you want to be performed.
#
# To save your results, simply hit the save button on the plot window that pops up.
#

# ui_responses = mainUI()  # This will open the UI and return the dictionary containing the results


def convert_file(conversion_extension):
    valid_extensions = ['.jpg', '.jpeg', '.png']

    if conversion_extension not in valid_extensions:
        print("ERROR: Invalid conversion extension")
    else:
        print("Success!")
