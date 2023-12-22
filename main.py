from flask import Flask, jsonify, request
from functools import wraps
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    connection = mysql.connector.connect(
        host='mysql-database.czrn9xpuxd4a.us-east-2.rds.amazonaws.com',
        port=3306,
        user='admin',
        password='Ea12345678!',
        database='6156service',
    )
    return connection

@app.route('/application/<int:postingID>')
def get_application(postingID):
    # connecting to database
    dbConnection = get_db_connection()
    # cursor object c
    c = dbConnection.cursor(dictionary=True)

    # get
    query = "SELECT * FROM application WHERE postingID = %s"
    try:
        c.execute(query, (postingID,))
        rows = c.fetchall()
        if rows is None:
            return jsonify({"message": "Application not found."}), 404
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({"An error occurred": str(e)}), 500
    finally:
        c.close()
        dbConnection.close()



@app.route('/application', methods=['POST'])
def create_application():
    # json dictionary
    create_data = request.json
    # connecting to database
    dbConnection = get_db_connection()
    # cursor object c
    c = dbConnection.cursor()

    check_query = "SELECT * FROM application WHERE studentID = %s AND postingID = %s"
    c.execute(check_query, (create_data['studentID'], create_data['postingID']))
    if c.fetchone():
        c.close()
        dbConnection.close()
        return jsonify({'error': 'Application already exists'}), 400
    
    else: # create
        query = """INSERT INTO application (postingID, studentID, applicationDate) VALUES (%s, %s, %s)"""
        insertValues = (
        create_data['postingID'],
        create_data['studentID'], 
        create_data['applicationDate'], 
        )
        c.execute(query, insertValues)
        dbConnection.commit()
        c.close()
        dbConnection.close()
        return jsonify({'message': 'Application created'}), 201

@app.route('/application/<int:postingID>', methods=['PUT'])
def update_application(postingID):
    # json dictionary
    update_data = request.json
    # connecting to database
    dbConnection = get_db_connection()
    # cursor object c
    c = dbConnection.cursor()
    # update
    applicationUpdate = """ UPDATE application SET studentID = %s, applicationDate = %s WHERE postingID = %s"""
    c.execute(applicationUpdate, (
        update_data['studentID'],
        update_data['applicationDate'],
        postingID
    ))
    dbConnection.commit()
    c.close()
    dbConnection.close()
    return jsonify({'message': 'Application updated'}), 200

@app.route('/application/<int:postingID>/<string:studentID>', methods=['DELETE'])
def delete_application(postingID,studentID):
    # connecting to database
    dbConnection = get_db_connection()
    # cursor object c
    c = dbConnection.cursor()

    # delete
    applicationDelete = "DELETE FROM application WHERE postingID = %s AND studentID = %s"
    try:
        c.execute(applicationDelete, (postingID, studentID))
        dbConnection.commit()
        if c.rowcount < 1:
            return jsonify({"Error": "No application found."}), 404
        else: 
            return jsonify({"Message": "Successfully deleted the application"}), 200
    except Exception as e:
        dbConnection.rollback()
        return jsonify({"An error occurred": str(e)}), 500

    finally:
        c.close()
        dbConnection.close()


@app.route('/')
def home():
    return "Welcome to my Flask app on Google App Engine!"

if __name__ == "__main__":
    app.run(debug=True)