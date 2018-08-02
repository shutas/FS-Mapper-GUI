"""BMapper: Assistance tool to map one dataset with another of common key."""

# Written by Shuta Suzuki (shutas@umich.edu)

import os
import re
import ast
from flask import Flask, render_template, url_for, request

# Main web app
app = Flask(__name__)

def reset_directory(dir_name):
    """Delete all files inside specified directory."""
    # Get all files in specified directory
    file_list = [os.path.join(dir_name, file) for file in os.listdir(dir_name)]
    
    # Delete those files
    for file in file_list:
        os.remove(file)


def purge_directory(dir_name):
    """Delete all REGEX_ files inside specified directory."""
    # Get all REGEX files from specified directory
    file_list = [os.path.join(dir_name, file) \
                 for file in os.listdir(dir_name) \
                 if file.startswith("REGEX_") and file.endswith(".txt")]
    
    # Delete those files
    for file in file_list:
        os.remove(file)


def escape_parenthesis(string):
    """Add escape characters for regex search."""
    # paren_list -> possible parenthesis; escaped_paren_list -> standardized
    paren_list = ["(", ")", "（", "）"]
    escaped_paren_list = ["\(", "\)"]
    
    # Replace matching parenthesis
    for i in range(4):
        string = string.replace(paren_list[i], escaped_paren_list[i % 2])
    
    # Return escaped string
    return string


def standardize_numbers(string):
    """Convert all fullwidth number strings to halfwidth number strings."""
    # Lists to iterate for replacement later
    halfwidth_num_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    fullwidth_num_list = ["０", "１", "２", "３", "４", "５", "６", "７", "８", "９"]

    # Replace all fullwidth numbers to halfwidth numbers
    for i in range(10):
        string = string.replace(fullwidth_num_list[i], halfwidth_num_list[i])

    # Return standardized string
    return string


def standardize_sutegana(string):
    """Convert all katakana-sutegana to upper case."""
    # Lists to iterate for replacement later
    sutegana_list = ["ァ", "ィ", "ゥ", "ェ", "ォ", "ッ", "ャ", "ュ", "ョ"]
    katakana_list = ["ア", "イ", "ウ", "エ", "オ", "ツ", "ヤ", "ユ", "ヨ"]

    # Replace all relevant lower case sutegana to upper case
    for i in range(9):
        string = string.replace(sutegana_list[i], katakana_list[i])

    # Return standardized string
    return string


def standardize(string):
    """Wrapper function for standardizing representation for strings."""
    # Standardizing functions
    string = standardize_numbers(string)
    string = standardize_sutegana(string)
    
    # Return standardized string
    return string


def regexify(database_dir):
    """Turn all criteria in database files as regular expressions."""
    # Get list of old REGEX files if found in database directory
    regex_file_list = [file for file in os.listdir(database_dir) \
                       if file.startswith("REGEX_") and file.endswith(".txt")]
    
    # Remove these old files
    for file in regex_file_list:
        os.remove(os.path.join(database_dir, file))

    # Get list of all database files (excluding blacklist file)
    file_list = [file for file in os.listdir(database_dir) \
                 if file.endswith(".txt") and file != "blacklist.txt"]
    
    # For each database file
    for file in file_list:

        # Open database file
        with open(os.path.join(database_dir, file), encoding="utf-16") as f1:
            
            # Create/open a new REGEX version of the database file
            with open(os.path.join(database_dir, "REGEX_" + file), encoding="utf-16", mode="a+") as f2:
                
                # Get the first line in original database file
                line = f1.readline().strip()
                
                # Until end of file
                while line:

                    # Database file should be a two-column format
                    try:
                        criteria, cell_code = line.split("\t")
                    
                    # Database file not formatted correctly
                    except ValueError:

                        # Gather error information
                        err_dict = {}
                        err_dict["file"] = file
                        err_dict["line"] = line

                        # Raise error to be caught in main
                        raise ValueError(err_dict)

                    # Preprocess criteria/item name
                    criteria = escape_parenthesis(standardize(criteria))

                    # Write to new REGEX file
                    f2.write("^" + criteria + "$" + "\t" + cell_code + "\n")

                    # Get next line
                    line = f1.readline().strip()

    # If there is a blacklist file in database directory
    if os.path.exists(os.path.join(database_dir, "blacklist.txt")):

        # Open blacklist file
        with open(os.path.join(database_dir, "blacklist.txt"), encoding="utf-16") as f3:

            # Create/open a new REGEX version of the blacklist file
            with open(os.path.join(database_dir, "REGEX_blacklist.txt"), encoding="utf-16", mode="a+") as f4:
                
                # Get the first line in original blacklist file
                line = f3.readline().strip()

                # Until end of file
                while line:

                    # Preprocess criteria/item name
                    line = escape_parenthesis(standardize(line))

                    # Write to new REGEX file
                    f4.write("^" + line + "$" + "\n")

                    # Get next line
                    line = f3.readline().strip()


def in_blacklist(string, blacklist):
    """Returns whether a specified string is in the database."""
    # Iterate through the blacklist
    for pattern in blacklist:

        # If found, return True
        if re.search(pattern, string):
            return True

    # Not found, return False
    return False


def lookup_database(string, database):
    """Returns cell_code for given key. Returns empty string otherwise."""
    # Iterate through the database
    for pattern, cell_code in database:

        # For pattern, take out ^ and $
        if re.search(pattern[1:-1], standardize(string)):
            return cell_code

    # Not found, return empty string
    return ""


def init_database(database_dir, blacklist, database):
    """Initialize database by loading data from files in database_dir"""
    # Construct blacklist
    if "blacklist.txt" in os.listdir(database_dir):
        with open(os.path.join(database_dir, "blacklist.txt"), encoding="utf-16") as file_ptr:
            line = file_ptr.readline().strip()
            while line:
                line = standardize(line)
                blacklist.add(line)
                line = file_ptr.readline().strip()

    # Construct database
    database_file_list = [file for file in os.listdir(database_dir) \
                          if file.startswith("REGEX_") and \
                          file.endswith(".txt") and \
                          file != "REGEX_blacklist.txt"]

    for file in database_file_list:
        #print(file)
        with open(os.path.join(database_dir, file), encoding="utf-16") as file_ptr:
            line = file_ptr.readline().strip()
            while line:

                criteria, cell_code = line.strip().split("\t")
                criteria = standardize(criteria)
                line = file_ptr.readline().strip()
                if in_blacklist(criteria, blacklist):
                    continue
                elif not lookup_database(criteria, database):
                    database.append((criteria, cell_code))
                else:
                    # Check criteria/cell_code pair is correct
                    if lookup_database(criteria, database) != cell_code:
                        err_dict = {}
                        err_dict["criteria"] = criteria[1:-1]
                        err_dict["cell_code"] = cell_code
                        err_dict["file"] = file[6:]
                        err_dict["old_cell_code"] = lookup_database(criteria, database)
                        raise KeyError(err_dict)


def map_cell_codes(input_dir, output_dir, database, mapped_count, total_count):
    """Map cell codes for all lines in files in input_dir."""
    file_list = [file for file in os.listdir(input_dir) if file.endswith(".txt")]

    for file in file_list:

        with open(os.path.join(input_dir, file), encoding="utf-16") as input_file_ptr:
            with open(os.path.join(output_dir, "MAPPED_" + file), encoding="utf-16", mode="a+") as output_file_ptr:
                line = input_file_ptr.readline().strip()
                while line:
                    try:
                        criteria, amount = line.strip().split("\t")
                    except ValueError:
                        err_dict = {}
                        err_dict["file"] = file
                        err_dict["line"] = line
                        raise ValueError(err_dict)
                    #print("criteria:", criteria, "amount:", amount)
                    cell_code = lookup_database(criteria, database)
                    if cell_code:
                        #print("Yup")
                        output_file_ptr.write(criteria + "\t" + amount + "\t" + cell_code + "\n")
                        mapped_count += 1
                        total_count += 1
                        #total = total + 1
                    else:
                        #print("Nope")
                        output_file_ptr.write(criteria + "\t" + amount + "\n")
                        total_count += 1
                        print(criteria)
                    line = input_file_ptr.readline().strip()

 
@app.route("/", methods=["GET", "POST"])
def main():
    """Driver program for BMapper."""
    # If data is submitted on the main page
    if request.method == "POST":

        # Directories
        input_dir = request.form["input_dir"]
        output_dir = request.form["output_dir"]
        database_dir = request.form["database_dir"]
        
        # Data structures
        database = [] # List of ("regex pattern", "cell code")
        blacklist = set() # Set of "regex pattern"
        
        # For statistical data
        mapped_count = 0
        total_count = 0

        # Driver program:)
        try:

            # Clean output directory
            reset_directory(output_dir)

            # Preprocess database files
            regexify(database_dir)

            # Load database
            init_database(database_dir, blacklist, database)

            # Process input files
            map_cell_codes(input_dir, output_dir, database, mapped_count, total_count)

            # Delete intermediate files
            purge_directory(database_dir)
            purge_directory(input_dir)

            # Success! Render processed page
            return render_template("processed.html")

        # Invalid directory
        except FileNotFoundError as err:
            
            # Error message
            err_msg = str(err)
            
            # Get directory name which is between single quotes
            invalid_dir = err_msg[err_msg.find("'") + 1: err_msg.rfind("'")]
            
            # jinja2 variables for rendering
            context = {}
            context["dirname"] = invalid_dir
            
            # Delete intermediate files
            if os.path.exists(database_dir):
                purge_directory(database_dir)
            if os.path.exists(input_dir):
                purge_directory(input_dir)

            # Render error page
            return render_template("invalid_directory.html", **context)
        
        # Invalid insertion to database
        except KeyError as err:

            # err is a dictionary
            context = ast.literal_eval(str(err))

            # Delete intermediate files
            purge_directory(database_dir)
            purge_directory(input_dir)

            # Render error page
            return render_template("invalid_value.html", **context)
    
        # Invalid formatting in input or database file
        except ValueError as err:

            # err is a dictionary
            context = ast.literal_eval(str(err))

            # Delete intermediate files
            purge_directory(database_dir)
            purge_directory(input_dir)

            # Render error page
            return render_template("invalid_format.html", **context)

    # Display main page
    return render_template("index.html")


if __name__ == "__main__":
    # Run app!
    app.run(debug=True)