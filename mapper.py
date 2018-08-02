from flask import Flask, render_template, url_for, request
import re
import shutil
import pandas as pd
import os
import ast

app = Flask(__name__)

def reset_directory(dir_name):
    """Delete all files inside specified directory."""
    file_list = [os.path.join(dir_name, file) for file in os.listdir(dir_name)]
    for file in file_list:
        os.remove(file)


def escape_parenthesis(string):
    paren_list = ["(", ")", "（", "）"]
    escaped_paren_list = ["\(", "\)"]
    
    for i in range(4):
        string = string.replace(paren_list[i], escaped_paren_list[i % 2])
    
    return string


def standardize_numbers(string):
    halfwidth_num_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    fullwidth_num_list = ["０", "１", "２", "３", "４", "５", "６", "７", "８", "９"]

    for i in range(10):
        string = string.replace(fullwidth_num_list[i], halfwidth_num_list[i])

    return string


def standardize_sutegana(string):
    sutegana_list = ["ァ", "ィ", "ゥ", "ェ", "ォ", "ッ", "ャ", "ュ", "ョ"]
    katakana_list = ["ア", "イ", "ウ", "エ", "オ", "ツ", "ヤ", "ユ", "ヨ"]

    for i in range(9):
        string = string.replace(sutegana_list[i], katakana_list[i])

    return string


def standardize(string):
    string = standardize_numbers(string)
    string = standardize_sutegana(string)
    return string


def split2_at_tab(line, filename):
    try:
        first, second = line.split("\t")
        return (first, second)

    except:
        return (None, None)


def regexify(database_dir):
    """Turn all criteria in database files as regular expressions."""
    regex_file_list = [file for file in os.listdir(database_dir) if file.startswith("REGEX_") and file.endswith(".txt")]
    for file in regex_file_list:
        os.remove(os.path.join(database_dir, file))


    file_list = [file for file in os.listdir(database_dir) if file.endswith(".txt") and file != "blacklist.txt"]
    for file in file_list:
        with open(os.path.join(database_dir, file), encoding="utf-16") as f1:
            with open(os.path.join(database_dir, "REGEX_" + file), encoding="utf-16", mode="a+") as f2:
                line = f1.readline().strip()
                while line:
                    criteria, cell_code = line.split("\t")
                    #print("criteria:", criteria)
                    #print("type of criteria:", type(criteria))
                    criteria = escape_parenthesis(standardize(criteria))
                    f2.write("^" + criteria + "$" + "\t" + cell_code + "\n")
                    line = f1.readline().strip()

    if os.path.exists(os.path.join(database_dir, "blacklist.txt")):
        with open(os.path.join(database_dir, "blacklist.txt"), encoding="utf-16") as f3:
            with open(os.path.join(database_dir, "REGEX_blacklist.txt"), encoding="utf-16", mode="a+") as f4:
                line = f3.readline().strip()
                while line:
                    line = escape_parenthesis(standardize(line))
                    f4.write("^" + line + "$" + "\n")
                    line = f3.readline().strip()

def in_blacklist(string, blacklist):
    for pattern in blacklist:
        if re.search(pattern, string):
            return True
    return False


def lookup_database(string, database):
    for pattern, cell_code in database:
        #print("pattern:", pattern, "|", "cell_code", cell_code)
        # For pattern, take out ^ and $
        if re.search(pattern[1:-1], string):
            return cell_code
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
    database_file_list = [file for file in os.listdir(database_dir) if file.startswith("REGEX_") and file.endswith(".txt") and file != "REGEX_blacklist.txt"]

    for file in database_file_list:
        #print(file)
        with open(os.path.join(database_dir, file), encoding="utf-16") as file_ptr:
            line = file_ptr.readline().strip()
            while line:
                #print("line:", line)
                criteria, cell_code = line.strip().split("\t")
                criteria = standardize(criteria)
                line = file_ptr.readline().strip()
                if in_blacklist(criteria, blacklist):
                    continue
                elif not lookup_database(criteria, database):
                    database.append((criteria, cell_code))
                else:
                    # Check criteria/cell_code pair is correct
                    '''try:
                        if lookup_database(criteria, database) != cell_code:
                            error_msg = "Conflicting cell code for " + criteria
                            raise ValueError(error_msg)'''
                    if lookup_database(criteria, database) != cell_code:
                        error_msg = "Conflicting cell code for " + criteria + " in " + file + "\n" +\
                        "            Tried to encode " + criteria + " as " + cell_code + "\n" +\
                        "            But " + criteria + " is already registered as " + lookup_database(criteria, database)
                        err_dict = {}
                        err_dict["criteria"] = criteria[1:-1]
                        err_dict["cell_code"] = cell_code
                        err_dict["file"] = file
                        err_dict["old_cell_code"] = lookup_database(criteria, database)
                        raise KeyError(err_dict)
                        #raise KeyError(error_msg)


def map_cell_codes(input_dir, output_dir, database, mapped_count, total_count):
    """Map cell codes for all lines in files in input_dir."""
    file_list = [file for file in os.listdir(input_dir) if file.endswith(".txt")]

    for file in file_list:

        with open(os.path.join(input_dir, file), encoding="utf-16") as input_file_ptr:
            with open(os.path.join(output_dir, "MAPPED_" + file), encoding="utf-16", mode="a+") as output_file_ptr:
                line = input_file_ptr.readline().strip()
                while line:
                    criteria, amount = line.strip().split("\t")
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
def hello():
    if request.method == "POST":
        input_dict = request.form
        #print(input_dict)
        input_dir = request.form["input_dir"]
        output_dir = request.form["output_dir"]
        database_dir = request.form["database_dir"]
        database = [] # List of ("regex pattern", "cell code")
        blacklist = set() # Set of "regex pattern"
        mapped_count = 0
        total_count = 0

        try:
            # Clean output directory
            reset_directory(output_dir)

            # Preprocess database files
            regexify(database_dir)

            # Load database
            init_database(database_dir, blacklist, database)
            print(database)
            # Process input files
            map_cell_codes(input_dir, output_dir, database, mapped_count, total_count)

            return render_template("processed.html")

        except FileNotFoundError as err:
            err_msg = str(err)
            invalid_dir = err_msg[err_msg.find("'") + 1: err_msg.rfind("'")]
            context = {}
            context["dirname"] = invalid_dir
            return render_template("invalid_directory.html", **context)
        
        except KeyError as err:
            context = ast.literal_eval(str(err))
            return render_template("invalid_value.html", **context)
    
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)