from mysql.connector import connect, cursor
from flask import Blueprint, Response, jsonify, render_template, flash, redirect, session, url_for, request, current_app
from fpdf import FPDF 
from flask_jwt_extended import decode_token, get_current_user, get_jwt_identity, jwt_required
from .forms import session_jwt_required

views = Blueprint('views', __name__)

""" All the webiste pages have been Routed here"""
#CMMS APPLIVATION HOME PAGE
@views.route('/', methods=['GET'])
def main():
    
    #This active_page will give the nav-link to check whether it home or not in HTML
    active_page = 'home'
    #This is used to give the Title of the Website 
    title = "CMMS Application"

    token = session.get('jwt_token')
        
    if token:
        try:
            decoded_token = decode_token(token)
            session['current_user'] = decoded_token['sub']
            flash('Welcome back!', 'info')
            return redirect(url_for('auth_forms.dashBoard'))
        except Exception as e:
            flash('Invalid or expired token. Please log in again.', 'danger')
            session.pop('jwt_token', None)
            return redirect(url_for('auth_forms.login'))
    else:
        return render_template('index.html', title = title, active_page = active_page)


# Route for adding a machine
@views.route('/machine')
@session_jwt_required
def macInsert():
    title = "Add Machine"
    connect = None
    cursor = None

    try:
        # Create the connection and cursor objects
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True) 

        # Fetch data from mac_category
        query = "SELECT mac_cat_code, mac_cat_name FROM mac_category"
        cursor.execute(query)
        category = cursor.fetchall()

        # Fetch data from mac_location
        query1 = "SELECT mac_loc_code, mac_loc_name FROM mac_location"
        cursor.execute(query1)
        location = cursor.fetchall()

    except Exception as e:
        # Handle exceptions and provide feedback
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('views.index'))  # Redirect to a safe page or home page
    
    finally:
        # Ensure both cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template('ins_machine.html', category=category, location=location, title=title)


# Route for adding a machine in the database
@views.route('/api/insert_mac', methods=['POST'])
@session_jwt_required
def insertMachine():
    connect = None
    cursor = None
    try:
        # Getting inputs from the Form
        _mac_code = request.form.get('inputCode')
        _mac_name = request.form.get('inputName')
        _mac_desc = request.form.get('inputDescription')
        _mac_cat_code = request.form.get('inputCategory')
        _mac_loc_code = request.form.get('inputLocation')

        # Validate the received values
        if _mac_code and _mac_name and _mac_desc and _mac_cat_code and _mac_loc_code:

            # Creating the connection and cursor objects for executing SQL queries
            connect = current_app.get_db_connection()
            cursor = connect.cursor() 

            # Execute the stored procedure
            cursor.callproc('ins_mac_master_sp', (_mac_code, _mac_name, _mac_desc, _mac_cat_code, _mac_loc_code))

            # Fetch all the rows
            data = cursor.fetchall()

            if len(data) == 0:
                connect.commit()  # Commit the transaction
                flash("Created Machine Successfully", "success")
                return redirect(url_for('views.viewMachine'))  # Redirect to the viewMachine route
            else:
                flash("Machine Exists", "danger")
                return redirect(url_for('views.viewMachine')) 

    except Exception as e:
        # Log the exception details for debugging
        print(f"Error: {str(e)}")
        flash("Error: Unable to process the request", "danger")
        return redirect(url_for('views.viewMachine')) 

    finally:
        # Close the cursor and connection to free resources
        if cursor:
            cursor.close()
        if connect:
            connect.close()

# Route for viewing the machines in the database
@views.route('/view_mac')
@session_jwt_required
def viewMachine():
    title = "View Machine"
    connect = None
    cursor = None
    machine = []

    try:
        # Create the connection object and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)
        
        # Fetch data from machine
        query = "SELECT * FROM mac_master_view ORDER BY mac_num;"
        cursor.execute(query)
        machine = cursor.fetchall()
    
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('index'))  # Redirect to a safe page or home page

    finally:
        # Ensure both cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("view_machine.html", machine=machine, title=title)

@views.route("/editMachine/<string:mac_code>", methods=['GET', 'POST'])
@session_jwt_required
def editMachine(mac_code):
    title = "Edit Machine"
    connect = None
    cursor = None
    
    try:
        # Create the connection and cursor objects
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True) 
        
        if request.method == 'POST':
            # Retrieve form data
            mac_name = request.form.get('inputName')
            mac_desc = request.form.get('inputDescription')
            mac_cat = request.form.get('inputCategory')
            mac_loc = request.form.get('inputLocation')
            
            # Update machine details
            sql = """
            UPDATE mac_master 
            SET mac_name = %s, mac_desc = %s, mac_cat_code = %s, mac_loc_code = %s 
            WHERE mac_code = %s
            """
            cursor.execute(sql, [mac_name, mac_desc, mac_cat, mac_loc, mac_code])
            connect.commit()  # Commit the transaction
            
            flash("Machine Updated Successfully", "success")
            return redirect(url_for('views.viewMachine'))
        
        # Fetch data for the form
        sql = "SELECT * FROM mac_master WHERE mac_code = %s"
        cursor.execute(sql, [mac_code])
        machine = cursor.fetchone()
        
        # Fetch categories and locations
        query = "SELECT mac_cat_code, mac_cat_name FROM mac_category"
        cursor.execute(query)
        category = cursor.fetchall()
        
        query1 = "SELECT mac_loc_code, mac_loc_name FROM mac_location"
        cursor.execute(query1)
        location = cursor.fetchall()
        
    except Exception as e:
        # Handle any exceptions and provide feedback
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('views.viewMachine'))
    
    finally:
        # Ensure both cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()
    
    return render_template("edit_machine.html", machine=machine, category=category, location=location, title=title)


@views.route("/deleteMachine/<string:mac_code>", methods=['GET', 'POST'])
@session_jwt_required
def deleteMachine(mac_code):
    connect = None
    cursor = None
    try:
        # Establish the connection and create a cursor with dictionary=True for results as dictionaries
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True) 
        
        # SQL statement to delete the machine
        sql = "DELETE FROM mac_master WHERE mac_code = %s"
        cursor.execute(sql, [mac_code])
        
        # Commit the transaction
        connect.commit()
        
        # Flash success message and redirect to viewMachine
        flash("Machine Deleted Successfully", "success")
        return redirect(url_for('views.viewMachine'))
    
    except Exception as e:
        # Handle exceptions and flash error message
        flash("Error: The machine has been entered in the Maintenance transaction", "danger")
        return redirect(url_for('views.viewMachine'))
    
    finally:
        # Ensure both cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

# Route for adding a location
@views.route('/location', methods=['GET', 'POST'])
@session_jwt_required
def addLocation():
    title = "Add Location"
    connect = None
    cursor = None

    if request.method == 'POST':
        try:
            _mac_loc_code = request.form.get('inputCode').upper()
            _mac_loc_name = request.form.get('inputName').upper()

            # Validate the received values
            if _mac_loc_code and _mac_loc_name:
                
                # Create the connection object and cursor
                connect = current_app.get_db_connection()
                cursor = connect.cursor()

                # Execute the stored procedure
                cursor.callproc('ins_mac_loc_sp', (_mac_loc_code, _mac_loc_name))
                
                # Fetch the result from the stored procedure
                data = cursor.fetchall()

                if len(data) == 0:
                    connect.commit()  # Commit the transaction
                    flash("Created Location Successfully", "success")
                    return redirect(url_for('views.viewLocation'))
                else:
                    flash("Location Exists", "danger")
                    return redirect(url_for('views.viewLocation'))

        except Exception as e:
            # Handle exceptions and provide feedback
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('views.viewLocation'))
        
        finally:
            # Ensure both cursor and connection are closed
            if cursor:
                cursor.close()
            if connect:
                connect.close()

    return render_template('ins_location.html', title=title)

# Route for viewing the list of location
@views.route('/view_loc')
@session_jwt_required
def viewLocation():
    title = "View Location"
    connect = None
    cursor = None
    location = []

    try:
        # Create the connection object and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)
        
        # Fetch data from mac_location
        query = "SELECT * FROM mac_location;"
        cursor.execute(query)
        location = cursor.fetchall()
    
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('views.index'))  # Redirect to a safe page or home page

    finally:
        # Ensure both cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("view_location.html", location=location, title=title)

# Route for updating a Location
@views.route("/editLocation/<string:mac_loc_code>", methods=['GET', 'POST'])
@session_jwt_required
def editLocation(mac_loc_code):
    title = "Edit Location"
    connect = None
    cursor = None
    location = None

    try:
        # Create connection and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)

        if request.method == 'POST':
            mac_loc_name = request.form.get('inputName').upper()

            # Update the location
            sql = "UPDATE mac_location SET mac_loc_name=%s WHERE mac_loc_code=%s"
            cursor.execute(sql, [mac_loc_name, mac_loc_code])
            connect.commit()

            flash("Location Updated Successfully", "success")
            return redirect(url_for('views.viewLocation'))

        # Fetch the location details for GET request
        sql = "SELECT * FROM mac_location WHERE mac_loc_code=%s"
        cursor.execute(sql, [mac_loc_code])
        location = cursor.fetchone()

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('views.viewLocation'))

    finally:
        # Ensure cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("edit_location.html", location=location, title=title)

# Route for adding a category
@views.route('/category', methods=['GET', 'POST'])
@session_jwt_required
def addCategory():
    title = "Add Category"
    connect = None
    cursor = None
    
    if request.method == 'POST':
        try:
            _mac_cat_code = request.form.get('inputCode').upper()
            _mac_cat_name = request.form.get('inputName').upper()

            # Validate the received values
            if _mac_cat_code and _mac_cat_name:
                
                # Create the connection and cursor objects
                connect = current_app.get_db_connection()
                cursor = connect.cursor()
                
                # Execute the stored procedure
                cursor.callproc('ins_mac_cat_sp', (_mac_cat_code, _mac_cat_name))
                
                # Fetch the result if the stored procedure returns data
                data = cursor.fetchall()

                if len(data) == 0:
                    connect.commit()  # Commit the transaction
                    flash("Created Category Successfully", "success")
                    return redirect(url_for('views.viewCategory'))  # Adjust to the actual route name
                else:
                    flash("Category Exists", "danger")
                    return redirect(url_for('views.viewCategory'))  # Adjust to the actual route name

        except Exception as e:
            # Handle exceptions and display an error message
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('views.viewCategory'))  # Adjust to the actual route name
        
        finally:
            # Ensure both cursor and connection are closed
            if cursor:
                cursor.close()
            if connect:
                connect.close()

    return render_template('ins_category.html', title=title)

# Route for viewing the list of categories
@views.route('/view_cat')
@session_jwt_required
def viewCategory():
        
    title = "View Category"
    connect = None
    cursor = None
    category = []

    try:
        # Create the connection object and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)
        
        # Fetch data from mac_category
        query = "SELECT * FROM mac_category;"
        cursor.execute(query)
        category = cursor.fetchall()
    
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('views.index'))  # Redirect to a safe page or home page

    finally:
        # Ensure both cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("view_category.html", category=category, title=title)

# Route for updating a Category
@views.route("/editCategory/<string:mac_cat_code>", methods=['GET', 'POST'])
@session_jwt_required
def editCategory(mac_cat_code):
    title = "Edit Category"
    connect = None
    cursor = None
    category = None

    try:
        # Create connection and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)

        if request.method == 'POST':
            mac_cat_name = request.form.get('inputName').upper()

            # Update the category
            sql = "UPDATE mac_category SET mac_cat_name=%s WHERE mac_cat_code=%s"
            cursor.execute(sql, [mac_cat_name, mac_cat_code])
            connect.commit()

            flash("Category Updated Successfully", "success")
            return redirect(url_for('views.viewCategory'))

        # Fetch the category details for GET request
        sql = "SELECT * FROM mac_category WHERE mac_cat_code=%s"
        cursor.execute(sql, [mac_cat_code])
        category = cursor.fetchone()

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('views.viewCategory'))

    finally:
        # Ensure cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("edit_category.html", category=category, title=title)

# Route for inserting a Maintenance Transaction
@views.route("/add_break", methods=['GET', 'POST'])
@session_jwt_required
def add_break():
    title = "Add Maintenance"
    connect = None
    cursor = None
    machine = None

    try:
        # Create the connection and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)

        if request.method == 'POST':
            # Fetch form data
            mac_code = request.form.get('inputMachine')
            trans_type = request.form.get('main')
            break_date = request.form.get('breakDate')
            start_date = request.form.get('startDate')
            end_date = request.form.get('endDate')
            production_time = request.form.get('productionTime')

            # Insert new maintenance record
            sql = """INSERT INTO mac_trans(mac_code, trans_type, trans_date, start_date, 
                      end_date, prod_loss_min, completed) 
                      VALUES (%s, %s, %s, %s, %s, %s, 0);"""
            cursor.execute(sql, [mac_code, trans_type, break_date, start_date, end_date, production_time])
            connect.commit()

            # Flash success message and redirect
            flash("Added Machine Maintenance", "success")
            return redirect(url_for('views.viewTrans'))

        # Fetch machines for GET request
        sql = "SELECT * FROM mac_master"
        cursor.execute(sql)
        machine = cursor.fetchall()

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('views.viewTrans'))

    finally:
        # Ensure cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("ins_maintenance.html", machine=machine, title=title)

#Route for Preventive Maintenance
@views.route('/add_preventive', methods=['GET', 'POST'])
@session_jwt_required
def add_preventive():
    title = "Add Preventive Maintenance"
    connect = None
    cursor = None
    machine = None

    try:
        # Create the connection and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)

        if request.method == 'POST':
            # Fetch form data
            machine_id = request.form['machine_id']
            task_name = request.form['task_name']
            description = request.form['description']
            schedule_date = request.form['schedule_date']

            # Insert new preventive maintenance task
            sql = """INSERT INTO MaintenanceTasks 
                     (machine_id, task_name, description, schedule_date, status) 
                     VALUES (%s, %s, %s, %s, 'Pending')"""
            cursor.execute(sql, (machine_id, task_name, description, schedule_date))
            connect.commit()

            # Flash success message and redirect
            flash('Preventive Maintenance Task Added', 'success')
            return redirect(url_for('views.viewTrans'))

        # Fetch machines for GET request
        sql = "SELECT * FROM mac_master"
        cursor.execute(sql)
        machine = cursor.fetchall()

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('views.viewTrans'))

    finally:
        # Ensure cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("ins_preventive.html", machine=machine, title=title)

#View Machine Transaction Route
@views.route('/view_trans')
@session_jwt_required
def viewTrans():
    title = "View Maintenance"
    connect = None
    cursor = None
    transactions = None

    try:
        # Create the connection and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)

        # Execute the query to fetch maintenance transactions
        query = "SELECT * FROM mac_trans_view ORDER BY trans_num;"
        cursor.execute(query)
        transactions = cursor.fetchall()

    except Exception as e:
        # Handle any errors during the query execution
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('index'))

    finally:
        # Ensure cursor and connection are closed to free resources
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("view_trans.html", transactions=transactions, title=title)

#Update Machine Transaction
@views.route("/editTrans/<string:trans_num>/<string:mac_code>", methods=['GET', 'POST'])
@session_jwt_required
def editTrans(trans_num, mac_code):
    title = "Edit Maintenance"
    connect = None
    cursor = None

    try:
        # Create the connection and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)

        if request.method == 'POST':
            # Retrieve form data
            mac_code = request.form.get('inputMachine')
            trans_type = request.form.get('main')
            break_date = request.form.get('breakDate')
            start_date = request.form.get('startDate')
            end_date = request.form.get('endDate')
            production_time = request.form.get('productionTime')
            completed = 1 if request.form.get('completed') == 'on' else 0
            
            # Update query
            sql = """
            UPDATE mac_trans 
            SET mac_code = %s, trans_type = %s, trans_date = %s, start_date = %s, end_date = %s, prod_loss_min = %s, completed = %s 
            WHERE trans_num = %s;
            """
            cursor.execute(sql, [mac_code, trans_type, break_date, start_date, end_date, production_time, completed, trans_num])
            connect.commit()

            flash("Machine Transaction Updated Successfully", "success")
            return redirect(url_for('views.viewTrans'))
        
        # Fetch transaction details for the form
        sql = "SELECT * FROM mac_trans WHERE trans_num = %s"
        cursor.execute(sql, [trans_num])
        transactions = cursor.fetchone()

        # Fetch machine list for the dropdown
        sql1 = "SELECT * FROM mac_master"
        cursor.execute(sql1)
        machine = cursor.fetchall()

    except Exception as e:
        # Handle the exception and display an error message
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('views.viewTrans'))
    
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("edit_trans.html", row=transactions, machine=machine, title=title)

#Displaying the Total Transactions of a Machine in a Report
@views.route("/report", methods=['GET', 'POST'])
@session_jwt_required
def report():
    title = "Report"
    connect = None
    cursor = None
    transactions = []
    
    try:
        # Create the connection and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)
        
        if request.method == 'POST':
            # Retrieve form data
            mac_code = request.form.get('inputMachine')
            start_date = request.form.get('startDate')
            end_date = request.form.get('endDate')
            
            # Query for fetching transactions based on the filter criteria
            query = """
                SELECT * FROM mac_trans_view 
                WHERE mac_code = %s 
                AND trans_date >= %s 
                AND trans_date <= %s;
            """
            cursor.execute(query, [mac_code, start_date, end_date])
            transactions = cursor.fetchall()
        
        # Fetch data from mac_master for the dropdown
        sql1 = "SELECT * FROM mac_master"
        cursor.execute(sql1)
        machine = cursor.fetchall()

    except Exception as e:
        # Handle any exceptions and display an error message
        flash(f"An error occurred: {str(e)}", "danger")
        transactions = []

    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template("report.html", machine=machine, transactions=transactions, title=title)

#Route for Data Visualization
@views.route('/chart')
@session_jwt_required
def chart():
    title = "Data Visualization"
    connect = None
    cursor = None
    
    try:
        # Create the connection and cursor
        connect = current_app.get_db_connection()
        cursor = connect.cursor(dictionary=True)
        
        # Query to fetch aggregated data
        query = """
            SELECT 
                mac_name, 
                SUM(total_break_hours) AS total_break_hours, 
                SUM(repair_hours) AS repair_hours, 
                SUM(prod_loss_min) AS prod_loss_min 
            FROM mac_trans_view 
            GROUP BY mac_name;
        """
        cursor.execute(query)
        data = cursor.fetchall()
    
    except Exception as e:
        # Handle any exceptions and display an error message
        flash(f"An error occurred: {str(e)}", "danger")
        data = []
    
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if connect:
            connect.close()

    return render_template('reportchart.html', data=data, title=title)

#Route to download the report as PDF
@views.route('/pdf', methods=['GET', 'POST'])
@session_jwt_required
def download_report():
    title = "Generate PDF"
    connection = None
    cursor = None

    if request.method == 'POST':
        report_type = request.form['report_type']
        
        try:
            # Establish the database connection
            connection = current_app.get_db_connection()
            cursor = connection.cursor(dictionary=True)

            if report_type == 'machine_data':
                cursor.execute("SELECT * FROM mac_master_view ORDER BY mac_num")
                result = cursor.fetchall()
                response = generate_machine_data_pdf(result)

            elif report_type == 'employee_data':
                cursor.execute("SELECT * FROM users ORDER BY user_id")
                result = cursor.fetchall()
                response = generate_employee_data_pdf(result)

            elif report_type == 'maintenance_data':
                cursor.execute("SELECT * FROM mac_trans_view ORDER BY trans_num")
                result = cursor.fetchall()
                response = generate_maintenance_data_pdf(result)

            elif report_type == 'summary_data':
                cursor.execute(
                    "SELECT mac_name, SUM(total_break_hours) AS total_break_hours, "
                    "SUM(repair_hours) AS repair_hours, SUM(prod_loss_min) AS prod_loss_min "
                    "FROM mac_trans_view GROUP BY mac_name"
                )
                result = cursor.fetchall()
                response = generate_summary_data_pdf(result)

            else:
                flash('Invalid report type selected.', 'danger')
                return redirect(url_for('views.download_report'))

            # flash(f'{report_type.replace("_", " ").capitalize()} report generated successfully!', 'success')
            return response

        except Exception as e:
            print(e)
            flash('An error occurred while generating the report.', 'danger')

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template('reportpdf.html', title=title)

# Helper functions for PDF generation

def generate_machine_data_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w - 2 * pdf.l_margin

    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(page_width, 0.0, 'Machine Data', align='C')
    pdf.ln(10)

    col_width = page_width / 3
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(col_width, 2 * pdf.font_size, 'Machine Name', border=1)
    pdf.cell(col_width, 2 * pdf.font_size, 'Category', border=1)
    pdf.cell(col_width, 2 * pdf.font_size, 'Location', border=1)
    pdf.ln()

    pdf.set_font('Courier', '', 10)
    for row in data:
        pdf.cell(col_width, pdf.font_size, row['mac_name'], border=1)
        pdf.cell(col_width, pdf.font_size, row['mac_cat_name'], border=1)
        pdf.cell(col_width, pdf.font_size, row['mac_loc_name'], border=1)
        pdf.ln()

    pdf.ln(10)
    pdf.set_font('Times', '', 10.0)
    pdf.cell(page_width, 0.0, '- End of report -', align='C')

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=machine_report.pdf'})

def generate_employee_data_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w - 2 * pdf.l_margin

    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(page_width, 0.0, 'Employee Data', align='C')
    pdf.ln(10)

    col_width = page_width / 4
    pdf.set_font('Times', 'B', 12.0)
    pdf.cell(col_width, 2 * pdf.font_size, 'Employee ID', border=1)
    pdf.cell(col_width, 2 * pdf.font_size, 'Employee Name', border=1)
    pdf.cell(col_width, 2 * pdf.font_size, 'Employee Email-ID', border=1)
    pdf.cell(col_width, 2 * pdf.font_size, 'Authority', border=1)
    pdf.ln()

    pdf.set_font('Courier', '', 10)
    for row in data:
        pdf.cell(col_width, pdf.font_size, str(row['user_id']), border=1)
        pdf.cell(col_width, pdf.font_size, row['user_name'], border=1)
        pdf.cell(col_width, pdf.font_size, row['user_email'], border=1)
        pdf.cell(col_width, pdf.font_size, row['user_level'], border=1)
        pdf.ln()

    pdf.ln(10)
    pdf.set_font('Times', '', 10.0)
    pdf.cell(page_width, 0.0, '- End of report -', align='C')

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=employee_report.pdf'})

def generate_maintenance_data_pdf(data):
    pdf = FPDF('L')
    pdf.add_page()

    pdf.set_font('Arial', 'B', 7)
    pdf.cell(30, 10, 'Transaction Num', 1)
    pdf.cell(20, 10, 'Machine Code', 1)
    pdf.cell(30, 10, 'Transaction Type', 1)
    pdf.cell(30, 10, 'Transaction Date', 1)
    pdf.cell(30, 10, 'Start Date', 1)
    pdf.cell(30, 10, 'End Date', 1)
    pdf.cell(30, 10, 'Production Time (min)', 1)
    pdf.cell(30, 10, 'Repair Hours', 1)
    pdf.cell(35, 10, 'Total Maintenance Hours', 1)
    pdf.ln()

    pdf.set_font('Arial', '', 7)
    for row in data:
        pdf.cell(30, 10, str(row['trans_num']), 1)
        pdf.cell(20, 10, row['mac_code'], 1)
        pdf.cell(30, 10, row['trans_type'], 1)
        pdf.cell(30, 10, str(row['trans_date']), 1)
        pdf.cell(30, 10, str(row['start_date']), 1)
        pdf.cell(30, 10, str(row['end_date']), 1)
        pdf.cell(30, 10, str(row['prod_loss_min']), 1)
        pdf.cell(30, 10, str(row['repair_hours']), 1)
        pdf.cell(35, 10, str(row['total_break_hours']), 1)
        pdf.ln()

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=transaction_report.pdf'})

def generate_summary_data_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    page_width = pdf.w - 2 * pdf.l_margin

    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(page_width, 0.0, 'Machine Maintenance Summary Data', align='C')
    pdf.ln(10)

    col_width = page_width / 100
    pdf.set_font('Times', 'B', 10)
    pdf.cell(col_width*35, 2 * pdf.font_size, 'Machine Name', border=1)
    pdf.cell(col_width*22, 2 * pdf.font_size, 'Total Breakdown Hours', border=1)
    pdf.cell(col_width*17, 2 * pdf.font_size, 'Total Repair Hours', border=1)
    pdf.cell(col_width*26, 2 * pdf.font_size, 'Total Production Loss Minutes', border=1)
    pdf.ln()

    pdf.set_font('Courier', '', 9)
    for row in data:
        pdf.cell(col_width*35, pdf.font_size, row['mac_name'], 1)
        pdf.cell(col_width*22, pdf.font_size, str(row['total_break_hours']), 1)
        pdf.cell(col_width*17, pdf.font_size, str(row['repair_hours']), 1)
        pdf.cell(col_width*26, pdf.font_size, str(row['prod_loss_min']), 1)
        pdf.ln()

    pdf.ln(10)
    pdf.set_font('Times', '', 10.0)
    pdf.cell(page_width, 0.0, '- End of report -', align='C')

    return Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                    headers={'Content-Disposition': 'attachment;filename=summary_report.pdf'})