from flask import Blueprint, Response, render_template, flash, redirect, url_for, request
from flask_login import login_user, login_required, logout_user, current_user, LoginManager,UserMixin
from fpdf import FPDF 
from . import db   # from __init__.py import db
from datetime import datetime, timedelta


views = Blueprint('views', __name__)

#CMMS Application FUNCTIONALITTIES
@views.route('/', methods=['GET'])
def main():
    
    #This active_page will give the nav-link to check whether it home or not in HTML
    active_page = 'home'
    #This is used to give the Title of the Website 
    title = "CMMS Application"

    return render_template('index.html', title = title, active_page = active_page)

# Route for adding a machine
@views.route('/machine')
@login_required
def macInsert():
    
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
def insertMachine():
    try:
        #Getting inputs from the Form
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
                return redirect(url_for('views.viewMachine')) 
            else:
                flash("Machine Exists", "danger")
                return redirect(url_for('views.viewMachine')) 

    except Exception as e:
        # Log the exception details for debugging
        print(f"Error: {str(e)}")
        flash("Error: Unable to process the request", "danger")
        return redirect(url_for('views.view_mac')) 

    finally:
        cur.close()

# Route for viewing the list of machines
@views.route('/view_mac')
@login_required
def viewMachine():

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
@login_required
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
                    return redirect(url_for('views.viewLocation')) 
                else:
                    # Display the prompt if the condition is false
                    flash("Location Exits", "danger")
                    return redirect(url_for('views.viewLocation')) 

        except Exception as e:
            # Display the prompt if the condition is unacceptable
            flash("Error. Enter 4 Characters in Location Code", "danger")
            return redirect(url_for('views.viewLocation')) 
        finally:
            cur.close()

    return render_template('ins_location.html', title = title)

# Route for viewing the list of location
@views.route('/view_loc')
@login_required
def viewLocation():

    title = "View Location"
    # Creating the cursor object for executing SQL queries with the connected MySQL database    
    con = db.connection.cursor()

    # Fetch data from mac_location
    query = "SELECT * FROM mac_location;"
    con.execute(query)
    location = con.fetchall()
    
    return render_template("view_location.html", location = location, title = title)

# Route for adding a category
@views.route('/category', methods=['GET','POST'])
@login_required
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
                    return redirect(url_for('views.viewCategory')) 
                else:
                    # Display the prompt if the condition is false
                    flash("Category Exists", "danger")
                    return redirect(url_for('views.viewCategory')) 
                
        except Exception as e:
            # Display the prompt if the condition is unacceptable
            flash("Error. Enter 2 Characters in Category Code", "danger")
            return redirect(url_for('views.view_cat')) 
        finally:
            cur.close()

    return render_template('ins_category.html', title = title)

# Route for viewing the list of categories
@views.route('/view_cat')
@login_required
def viewCategory():
        
    title = "View Category"
    con = db.connection.cursor()

    # Fetch data from mac_category
    query = "SELECT * FROM mac_category;"
    con.execute(query)
    category = con.fetchall()
    
    return render_template("view_category.html", category = category, title = title)

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
        return redirect(url_for('views.viewMachine')) 

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
        return redirect(url_for('views.viewMachine')) 
    
    except Exception as e:
        # Display the prompt if the condition is unacceptable
        flash("Error. That the Machine has been entered in the Maintenance transaction", "danger")
        return redirect(url_for('views.viewMachine')) 

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
        return redirect(url_for('views.viewCategory')) 

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
        return redirect(url_for('views.viewLocation')) 

    sql = "select * from mac_location where mac_loc_code=%s"
    con.execute(sql, [mac_loc_code])
    location=con.fetchone()
    con.close()

    return render_template("edit_location.html", location = location, title = title)

# Route for inserting a Maintenance Transaction
@views.route("/add_break", methods=['GET','POST'])
@login_required
def add_break():

    title = "Add Maintenance"
    con = db.connection.cursor() 
    if request.method == 'POST':
         
        mac_code = request.form.get('inputMachine')
        trans_type = request.form.get('main')
        break_date = request.form.get('breakDate')
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')
        production_time = request.form.get('productionTime')

        sql = "insert mac_trans(mac_code,trans_type,trans_date,start_date,end_date,prod_loss_min,completed) values(%s,%s,%s,%s,%s,%s,0);"
        con.execute(sql, [mac_code, trans_type, break_date, start_date, end_date, production_time])
        db.connection.commit()

        con.close()
        # Flash message
        flash("Added Machine Maintenance", "success")
        return redirect(url_for('views.viewTrans')) 
    
    sql = "select * from mac_master"
    con.execute(sql)
    machine = con.fetchall()
    
    return render_template("ins_maintenance.html", machine = machine, title = title)

# @views.route('/add_preventive_maintenance_task', methods=['POST'])
@views.route('/add_preventive', methods=['GET','POST'])
@login_required
def add_preventive():

    title = "Add Preventive Maintenance"
    con = db.connection.cursor()

    if request.method == 'POST':
        machine_id = request.form['machine_id']
        task_name = request.form['task_name']
        description = request.form['description']
        schedule_date = request.form['schedule_date']
        cursor = db.connection.cursor()

        cursor.execute("INSERT INTO MaintenanceTasks (machine_id, task_name, description, schedule_date, status) VALUES (%s, %s, %s, %s, 'Pending')", (machine_id, task_name, description, schedule_date))
        
        db.connection.commit()
        flash('Preventive Maintenance Task Added')
        return redirect(url_for('views.viewTrans'))   

    sql = "select * from mac_master"
    con.execute(sql)
    machine = con.fetchall()
    
    return render_template("preventive.html", machine = machine, title = title)

#View Maintenance Route
@views.route('/view_trans')
@login_required
def viewTrans():
    
    title = "View Maintenance"    
    con = db.connection.cursor()
    query = "select * from mac_trans_view;"
    con.execute(query)
    transactions = con.fetchall()
    
    return render_template("view_trans.html", transactions=transactions, title=title)

#Update Transcation
@views.route("/editTrans/<string:trans_num>/<string:mac_code>", methods=['GET','POST'])
def editTrans(trans_num,mac_code):

    title = "Edit Maintenance"
    con = db.connection.cursor()
    if request.method == 'POST':
        try:
            mac_code = request.form.get('inputMachine')
            trans_type = request.form.get('main')
            break_date = request.form.get('breakDate')
            start_date = request.form.get('startDate')
            end_date = request.form.get('endDate')
            production_time = request.form.get('productionTime')
            completed = 0
            if request.form.get('completed') == 'on':
                completed = 1

            sql = "update mac_trans set mac_code = %s, trans_type = %s, trans_date = %s, start_date = %s, end_date = %s,prod_loss_min = %s, completed=%s where trans_num=%s;"
            con.execute(sql, [mac_code, trans_type, break_date, start_date, end_date, production_time, completed, trans_num])
            db.connection.commit()

            con.close()

            flash("UPDATED MACHINE TRANSACTION", "success")
            return redirect(url_for('views.viewTrans')) 

        except Exception as e:
            # handle the exception
            flash("An error occurred:", "danger")
            return redirect(url_for('views.viewTrans')) 

        
    sql = "select * from mac_trans where trans_num=%s"
    con.execute(sql, [trans_num])
    transactions=con.fetchone()

    sql1 = "select * from mac_master"
    con.execute(sql1)
    machine=con.fetchall()
    con.close()

    return render_template("edit_trans.html",row = transactions, machine=machine, title=title)

#Displaying the Total Transactions of a Machine
@views.route("/report",methods=['GET','POST'])
@login_required
def report():

    title = "Report"
    con = db.connection.cursor()
    if request.method == 'POST':
        try:
            mac_code = request.form.get('inputMachine')
            start_date = request.form.get('startDate')
            end_date = request.form.get('endDate')

            query = "select * from mac_trans_view where mac_code = %s AND trans_date >= %s AND trans_date <= %s;"
            con.execute(query, [mac_code,start_date,end_date])
            transactions = con.fetchall()

            # Fetch data from mac_master
            sql1 = "select * from mac_master"
            con.execute(sql1)
            machine=con.fetchall()
            con.close()
            
        except Exception as e:
            # handle the exception
            print("An error occurred:", str(e))
            transactions = []
            
        return render_template("report.html", machine=machine, transactions=transactions)

    sql1 = "select * from mac_master"
    con.execute(sql1)
    machine=con.fetchall()
    con.close()

    return render_template("report.html",machine=machine, title=title)

@views.route('/chart')
@login_required
def chart():
    title = "Data Visualization"
    cursor = db.connection.cursor()
    cursor.execute("Select mac_name, sum(total_break_hours) as total_break_hours, sum(repair_hours) as repair_hours, sum(prod_loss_min) as prod_loss_min from mac_trans_view GROUP BY mac_name;")
    data = cursor.fetchall()
    return render_template('reportchart.html', data=data, title=title)

@views.route('/pdf', methods=['GET','POST'])
def download_report():
    title = "Generate PDF"
    if request.method == 'POST':
        # Inputs the user command
        report_type = request.form['report_type']
        cursor = None
        try:
            cursor = db.connection.cursor()

            # Checks whether the user command of 'report_type' is machine_data 
            if report_type == 'machine_data':
                cursor.execute("SELECT * FROM mac_master_view ORDER BY mac_num")
                result = cursor.fetchall()

                pdf = FPDF()
                pdf.add_page()

                page_width = pdf.w - 2 * pdf.l_margin

                pdf.set_font('Times', 'B', 14.0)
                pdf.cell(page_width, 0.0, 'Machine Data', align='C')
                pdf.ln(10)

                col_width = page_width / 3
                # Set the default height for all cells to 20 units
                pdf.font_size = 20

                # Set the font to bold and print column names
                pdf.set_font('Times', 'B', 12.0)
                pdf.cell(col_width, 2 * pdf.font_size, 'Machine Name', border=1)
                pdf.cell(col_width, 2 * pdf.font_size, 'Category', border=1)
                pdf.cell(col_width, 2 * pdf.font_size, 'Location', border=1)
                pdf.ln()

                pdf.set_font('Courier', '', 10)
                pdf.font_size = 10

                for row in result:
                    pdf.cell(col_width, pdf.font_size, row['mac_name'], border=1)
                    pdf.cell(col_width, pdf.font_size, row['mac_cat_name'], border=1)
                    pdf.cell(col_width, pdf.font_size, row['mac_loc_name'], border=1)
                    pdf.ln()

                pdf.ln(10)

                pdf.set_font('Times', '', 10.0)
                pdf.cell(page_width, 0.0, '- End of report -', align='C')
                
                response = Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                                    headers={'Content-Disposition': 'attachment;filename=machine_report.pdf'})
                
                flash('Machine report generated successfully!', 'success')
                return response
                                       
            # Checks whether the user command of 'report_type' is employee_data
            elif report_type == 'employee_data':
                cursor = db.connection.cursor()
                cursor.execute("SELECT * FROM users ORDER BY user_id")
                result = cursor.fetchall()

                pdf = FPDF()
                pdf.add_page()

                page_width = pdf.w - 2 * pdf.l_margin

                pdf.set_font('Times', 'B', 14.0)
                pdf.cell(page_width, 0.0, 'Employee Data', align='C')
                pdf.ln(10)

                #Display the columns into the size of 4 columns
                col_width = page_width / 4
                # Set the default height for all cells to 20 units
                pdf.font_size = 20

                # Set the font to bold and print column names
                pdf.set_font('Times', 'B', 12.0)
                pdf.cell(col_width, 2 * pdf.font_size, 'Employee ID', border=1)
                pdf.cell(col_width, 2 * pdf.font_size, 'Employee Name', border=1)
                pdf.cell(col_width, 2 * pdf.font_size, 'Employee Email-ID', border=1)
                pdf.cell(col_width, 2 * pdf.font_size, 'Authority', border=1)
                pdf.ln()

                pdf.set_font('Courier', '', 10)
                pdf.font_size = 10

                for row in result:
                    pdf.cell(col_width, pdf.font_size, str(row['user_id']), border=1)
                    pdf.cell(col_width, pdf.font_size, row['user_name'], border=1)
                    pdf.cell(col_width, pdf.font_size, row['user_email'], border=1)
                    pdf.cell(col_width, pdf.font_size, row['user_level'], border=1)
                    pdf.ln()

                pdf.ln(10)

                pdf.set_font('Times', '', 10.0)
                pdf.cell(page_width, 0.0, '- End of report -', align='C')

                response = Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=employee_report.pdf'})
                
                flash('Employee Report generated successfully!', 'success')
                return response

            # Checks whether the user command of 'report_type' is maintenance_data
            elif report_type == 'maintenance_data':
                cursor = db.connection.cursor()
                cursor.execute("SELECT * FROM mac_trans_view ORDER BY trans_num")
                result = cursor.fetchall()

                class PDF(FPDF):
                    pass

                pdf = PDF(orientation='L')
                pdf.add_page()

                # Set font and font size
                pdf.set_font('Arial', 'B', 7)

                # Add table header
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

                # Set font and font size for data rows
                pdf.set_font('Arial', '', 7)

                # Add table rows
                for row in result:
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

                # Output PDF as a response
                response = Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf',
                                headers={'Content-Disposition': 'attachment;filename=transaction_report.pdf'})
                
                flash('Transaction Report generated successfully!', 'success')
                return response
                   
            # Checks whether the user command of 'report_type' is summary_data
            elif report_type == 'summary_data':
                cursor = db.connection.cursor()
                cursor.execute("Select mac_name, sum(total_break_hours) as total_break_hours, sum(repair_hours) as repair_hours, sum(prod_loss_min) as prod_loss_min from mac_trans_view GROUP BY mac_name;")
                result = cursor.fetchall()

                pdf = FPDF()
                pdf.add_page()

                page_width = pdf.w - 2 * pdf.l_margin

                pdf.set_font('Times', 'B', 14.0)
                pdf.cell(page_width, 0.0, 'Machine Maintenance Summary Data', align='C')
                pdf.ln(10)

                col_width = page_width / 100
                # Set the default height for all cells to 12 units
                pdf.font_size = 12

                # Set the font to bold and print column names
                pdf.set_font('Times', 'B', 10)
                pdf.cell(col_width*35, 2 * pdf.font_size, 'Machine Name', border=1)
                pdf.cell(col_width*22, 2 * pdf.font_size, 'Total Breakdown Hours', border=1)
                pdf.cell(col_width*17, 2 * pdf.font_size, 'Total Repair Hours', border=1)
                pdf.cell(col_width*26, 2 * pdf.font_size, 'Total Production Loss Minutes', border=1)

                pdf.ln()

                pdf.set_font('Courier', '', 9)
                pdf.font_size = 10

                for row in result:
                    pdf.cell(col_width*35, pdf.font_size, row['mac_name'], 1)
                    pdf.cell(col_width*22, pdf.font_size, str(row['total_break_hours']), 1)
                    pdf.cell(col_width*17, pdf.font_size, str(row['repair_hours']), 1)
                    pdf.cell(col_width*26, pdf.font_size, str(row['prod_loss_min']), 1)
                    pdf.ln()

                pdf.ln(10)

                pdf.set_font('Times', '', 10.0)
                pdf.cell(page_width, 0.0, '- End of report -', align='C')

                response = Response(pdf.output(dest='S').encode('latin-1'), mimetype='application/pdf', headers={'Content-Disposition': 'attachment;filename=summary_report.pdf'})
                
                flash('Summary Report generated successfully!', 'success')
                return response
        
        except Exception as e:
            print(e)
            flash('An error occurred while generating the report.', 'danger')
        finally:
            if cursor:
                cursor.close()
    else:
        return render_template('reportpdf.html',title=title)
    
    return redirect(url_for('views.download_report'))