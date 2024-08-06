from flask import Blueprint, render_template, flash, jsonify, redirect, url_for, request    
from . import db   # from __init__.py import db
views = Blueprint('views', __name__)

#CMMS Application FUNCTIONALITTIES
@views.route('/', methods=['GET'])
def main():
    
    #This active_page will give the nav-link to check whether it home or not in HTML
    active_page = 'home'
    #This is used in navbar to give the Title of the Website
    title = "CMMS Application"

    return render_template('index.html', title = title, active_page = active_page)

# Route for adding a machine
@views.route('/machine')
def showInsert():
    
    title = "Add Machine"

    # Creating the cursor object with dictionary cursor
    con = db.connection.cursor()

    # Fetch data from mac_category
    query = "SELECT mac_cat_code, mac_cat_name FROM mac_category"
    con.execute(query)
    category = con.fetchall()

    # Fetch data from mac_location
    query1 = "SELECT mac_loc_code, mac_loc_name FROM mac_location"
    con.execute(query1)
    location = con.fetchall()

    return render_template('ins_machine.html', category = category, location = location, title = title)

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
                flash("Created Machine Successfully", "success")
                return redirect(url_for('views.view_mac')) 
            else:
                flash("Machine Exists", "danger")
                return redirect(url_for('views.view_mac')) 

    except Exception as e:
        # Log the exception details for debugging
        print(f"Error: {str(e)}")
        flash("Error: Unable to process the request", "danger")
        return redirect(url_for('views.view_mac')) 

    finally:
        cur.close()

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
    
    return render_template("view_machine.html", machine = machine, title = title)

# Route for adding a location
@views.route('/location', methods=['GET','POST'])
def addLocation():
    
    title = "Add Location"
    if request.method == 'POST':
        try:
            _mac_loc_code = request.form.get('inputCode').upper()
            _mac_loc_name = request.form.get('inputName').upper()

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
                    flash("Created Location Successfully", "success")
                    return redirect(url_for('views.view_loc')) 
                else:
                    # Display the prompt if the condition is false
                    flash("Location Exits", "danger")
                    return redirect(url_for('views.view_loc')) 

        except Exception as e:
            # Display the prompt if the condition is unacceptable
            flash("Error. Enter 4 Characters in Location Code", "danger")
            return redirect(url_for('views.view_loc')) 
        finally:
            cur.close()

    return render_template('ins_location.html', title = title)

# Route for adding a category
@views.route('/category', methods=['GET','POST'])
def addCategory():
    
    title = "Add Category"
    if request.method == 'POST':
        try:
            _mac_cat_code = request.form.get('inputCode').upper()
            _mac_cat_name = request.form.get('inputName').upper()

            # Validate the received values
            if _mac_cat_code and _mac_cat_name :
                
                # Creating the cursor object for executing SQL queries with the connected MySQL database 
                cur = db.connection.cursor()

                #Execute the stored procedure
                cur.callproc('ins_mac_cat_sp', ( _mac_cat_code, _mac_cat_name))
                data = cur.fetchall()

                if len(data) == 0:
                    db.connection.commit()
                    # Display the prompt if the condition is true
                    flash("Created Category Successfully", "success")
                    return redirect(url_for('views.view_cat')) 
                else:
                    # Display the prompt if the condition is false
                    flash("Category Exists", "danger")
                    return redirect(url_for('views.view_cat')) 
                
        except Exception as e:
            # Display the prompt if the condition is unacceptable
            flash("Error. Enter 2 Characters in Category Code", "danger")
            return redirect(url_for('views.view_cat')) 
        finally:
            cur.close()

    return render_template('ins_category.html', title = title)

# Route for viewing the list of categories
@views.route('/view_cat')
def view_cat():
        
    title = "View Category"
    # Creating the cursor object for executing SQL queries with the connected MySQL database    
    # Creating the cursor object with dictionary cursor
    con = db.connection.cursor()

    # Fetch data from mac_category
    query = "SELECT * FROM mac_category;"
    con.execute(query)
    category = con.fetchall()
    
    return render_template("view_category.html", category = category, title = title)

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
    
    return render_template("view_location.html", location = location, title = title)

# Route for updating a machine
@views.route("/editMachine/<string:mac_code>",methods=['GET','POST'])
def editMachine(mac_code):

    title = "Edit Machine"
    # Creating the cursor object for executing SQL queries with the connected MySQL database
    con = db.connection.cursor()
    
    if request.method == 'POST':

        mac_name = request.form.get('inputName')
        mac_desc = request.form.get('inputDescription')
        mac_cat = request.form.get('inputCategory')
        mac_loc = request.form.get('inputLocation')

        sql = "update mac_master set mac_name=%s, mac_desc=%s, mac_cat_code=%s, mac_loc_code=%s where mac_code=%s"
        con.execute(sql, [mac_name, mac_desc, mac_cat, mac_loc, mac_code])
        db.connection.commit()

        con.close()

        # Flash message
        flash("Machine Updated Successfully", "success")
        return redirect(url_for('views.view_mac')) 

    # Fetch data from mac_master
    sql = "select * from mac_master where mac_code=%s"
    con.execute(sql, [mac_code])
    machine=con.fetchone()

    # Fetch data from mac_category
    query = "SELECT mac_cat_code, mac_cat_name FROM mac_category"
    con.execute(query)
    category = con.fetchall()

    # Fetch data from mac_location
    query1 = "SELECT mac_loc_code, mac_loc_name FROM mac_location"
    con.execute(query1)
    location = con.fetchall()

    #Closing the connection
    con.close()

    return render_template("edit_machine.html", machine = machine, category = category, location = location, title = title)

# Route for deleting a Machine
@views.route("/deleteMachine/<string:mac_code>",methods=['GET','POST'])
def deleteMachine(mac_code):

    try:
        con = db.connection.cursor()
        sql = "Delete from mac_master where mac_code=%s"
        con.execute(sql, [mac_code])
        db.connection.commit()
        con.close()

        flash("Machine Deleted Successfully", "success")
        return redirect(url_for('views.view_mac')) 
    
    except Exception as e:
        # Display the prompt if the condition is unacceptable
        flash("Error. That the Machine has been entered in the Maintenance transaction", "danger")
        return redirect(url_for('views.view_mac')) 

# Route for updating a Category
@views.route("/editCategory/<string:mac_cat_code>",methods=['GET','POST'])
def editCategory(mac_cat_code):
    
    title = "Edit Category"
    con = db.connection.cursor()
    if request.method == 'POST':

        mac_cat_name = request.form.get('inputName').upper()
        
        sql = "update mac_category set mac_cat_name=%s where mac_cat_code=%s"
        con.execute(sql, [mac_cat_name, mac_cat_code])
        db.connection.commit()

        con.close()
        # Flash message
        flash("Category Updated Successfully", "success")
        return redirect(url_for('views.view_cat')) 

    sql = "select * from mac_category where mac_cat_code=%s"
    con.execute(sql, [mac_cat_code])
    category=con.fetchone()
    con.close()

    return render_template("edit_category.html", category = category, title = title)

# Route for updating a Location
@views.route("/editLocation/<string:mac_loc_code>",methods=['GET','POST'])
def editLocation(mac_loc_code):
    
    title = "Edit Location"
    con = db.connection.cursor()
    if request.method == 'POST':

        mac_loc_name = request.form.get('inputName').upper()
        
        sql = "update mac_location set mac_loc_name=%s where mac_loc_code=%s"
        con.execute(sql, [mac_loc_name,mac_loc_code])
        db.connection.commit()

        con.close()
        # Flash message
        flash("Location Updated Successfully", "success")
        return redirect(url_for('views.view_loc')) 

    sql = "select * from mac_location where mac_loc_code=%s"
    con.execute(sql, [mac_loc_code])
    location=con.fetchone()
    con.close()

    return render_template("edit_location.html", location = location, title = title)
