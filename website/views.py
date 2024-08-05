from flask import Blueprint, render_template, flash, jsonify, redirect, url_for, request    
from . import db   # from __init__.py import db
views = Blueprint('views', __name__)

#CMMS viewsLICATION FUNCTIONALITTIES
@views.route('/', methods=['GET'])
def main():
    
    #This active_page will give the nav-link to check whether it home or not in HTML
    active_page = 'home'
    #This is used in navbar to give the Title of the Website
    title = "CMMS viewslication"

    return render_template('index.html', title=title, active_page=active_page)

# Route for adding a machine
@views.route('/machine')
def showInsert():
    
    title = "Add Machine"

    # Creating the cursor object for executing SQL queries with the connected MySQL database 
    con = db.connection.cursor()

    # Fetch data from mac_category
    query = "SELECT mac_cat_code, mac_cat_name FROM mac_category"
    con.execute(query)
    category = con.fetchall()

    # Fetch data from mac_location
    query1 = "SELECT mac_loc_code, mac_loc_name FROM mac_location"
    con.execute(query1)
    location = con.fetchall()

    return render_template('ins_machine.html', category=category, location=location, title=title)

# Route for adding a machine in the database
@views.route('/api/insert_mac', methods=['POST'])
def insert_mac():
    try:
        #Getting inputs from the 
        _mac_code = request.form.get('inputCode')
        _mac_name = request.form.get('inputName')
        _mac_desc = request.form.get('inputDescription')
        _mac_cat_code = request.form.get('inputCategory')
        _mac_loc_code = request.form.get('inputLocation')

        # Validate the received values
        if _mac_code and _mac_name and _mac_desc and _mac_cat_code and _mac_loc_code:

            # Creating the cursor object for executing SQL queries with the connected MySQL database 
            cur = db.connection.cursor()

            # Execute the stored procedure
            cur.callproc('ins_mac_master_sp', (_mac_code, _mac_name, _mac_desc, _mac_cat_code, _mac_loc_code))

            # Fetch all the rows
            data = cur.fetchall()

            if len(data) == 0:
                db.connection.commit()
                # Display the prompt if the condition is true
                return '''
                <script>
                    window.alert("Machine Created Successfully");
                    window.location.href = "/view_mac";
                </script>
                '''
            else:
                # Display the prompt if the condition is false
                return '''
                <script>
                    window.alert("Machine Exists");
                    window.location.href = "/machine";
                </script>
                '''
        else:
            return '''
                <script>
                    window.alert("Enter the required fields");
                </script>
                '''
    except Exception as e:
        return '''
                <script>
                    window.alert("Error");
                </script>
                '''
    finally:
        cur.close()

# Route for adding a location
@views.route('/location', methods=['GET','POST'])
def addLocation():
    
    title = "Add Location"
    if request.method == 'POST':
        try:
            _mac_loc_code = request.form.get('inputCode')
            _mac_loc_name = request.form.get('inputName')

            # Validate the received values
            if _mac_loc_code and _mac_loc_name :

                # Creating the cursor object for executing SQL queries with the connected MySQL database 
                cur = db.connection.cursor()

                #Execute the stored procedure 
                cur.callproc('ins_mac_loc_sp', ( _mac_loc_code, _mac_loc_name))
                data = cur.fetchall()

                if len(data) == 0:
                    db.connection.commit()
                    # Display the prompt if the condition is true
                    return '''
                    <script>
                        window.alert("Created a Location Successfully");
                        window.location.href = "/view_loc";
                    </script>
                    '''
                else:
                    # Display the prompt if the condition is false
                    return '''
                    <script>
                        window.alert("Location Exists");
                        window.location.href = "/view_loc";
                    </script>
                    '''
            else:
                return '''
                    <script>
                        window.alert("Enter the required fields");
                    </script>
                    '''
        except Exception as e:
            return '''
                    <script>
                        window.alert("Error");
                    </script>
                    '''
        finally:
            cur.close()

    return render_template('ins_location.html', title=title)

# Route for viewing the list of machines
@views.route('/view_mac')
def view_mac():

    title = "View Machine"
    # Creating the cursor object for executing SQL queries with the connected MySQL database    
    cur = db.connection.cursor()

    # Fetch data from machine
    query = "SELECT * FROM mac_master_view order by mac_num;"
    cur.execute(query)
    machine = cur.fetchall()
    
    return render_template("view_machine.html",machine=machine, title = title)

# Route for viewing the list of categories
@views.route('/view_cat')
def view_cat():
        
    title = "View Category"
    # Creating the cursor object for executing SQL queries with the connected MySQL database    
    con = db.connection.cursor()

    # Fetch data from mac_category
    query = "SELECT * FROM mac_category;"
    con.execute(query)
    category = con.fetchall()
    
    return render_template("view_category.html",category=category, title=title)

# Route for viewing the list of location
@views.route('/view_loc')
def view_loc():

    title = "View Location"
    # Creating the cursor object for executing SQL queries with the connected MySQL database    
    con = db.connection.cursor()

    # Fetch data from mac_location
    query = "SELECT * FROM mac_location;"
    con.execute(query)
    location = con.fetchall()
    
    return render_template("view_location.html",location=location, title=title)
