from flask import Flask, jsonify, request
import sqlite3
import logging

app = Flask(__name__)

#Logging configuration
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Establish database connection
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn

#API Endpoints

# Endpoints to view all students
@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    logging.info("GET /students - fetched all students")
    return jsonify([dict(s) for s in students]), 200


# Endpoint to view a single student by ID
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    conn.close()
    if student is None:
        logging.warning(f"GET /students/{id} - student not found")
        return jsonify({"error": "Student not found"}), 404
    logging.info(f"GET /students/{id} - fetched student successfully")
    return jsonify(dict(student)), 200


# endpoint to add new students (single or multiple)
@app.route('/students', methods=['POST'])
def add_students():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is empty"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    added_count = 0

    try:
        # 🧠 CASE 1: If multiple students (list)
        if isinstance(data, list):
            for student in data:
                name = student.get("name")
                course = student.get("course")
                email = student.get("email")

                if not name or not course or not email:
                    conn.rollback()
                    return jsonify({"error": "Each record must have name, course, and email"}), 400

                cursor.execute('''
                    INSERT INTO students (name, course, email, phone, age, gender, address)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    name,
                    course,
                    email,
                    student.get("phone"),
                    student.get("age"),
                    student.get("gender"),
                    student.get("address")
                ))
                added_count += 1

            conn.commit()
            logging.info(f"POST /students - Added {added_count} students (bulk)")
            return jsonify({"message": f"{added_count} students added successfully!"}), 201

        # 🧠 CASE 2: If single student (dict)
        elif isinstance(data, dict):
            name = data.get("name")
            course = data.get("course")
            email = data.get("email")

            if not name or not course or not email:
                return jsonify({"error": "Missing required fields: name, course, or email"}), 400

            cursor.execute('''
                INSERT INTO students (name, course, email, phone, age, gender, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                name,
                course,
                email,
                data.get("phone"),
                data.get("age"),
                data.get("gender"),
                data.get("address")
            ))

            conn.commit()
            logging.info(f"POST /students - Added single student: {name}")
            return jsonify({"message": "Student added successfully!"}), 201

        else:
            return jsonify({"error": "Invalid JSON format"}), 400

    except sqlite3.IntegrityError:
        conn.rollback()
        logging.error("Duplicate email in request data")
        return jsonify({"error": "Email already exists"}), 400

    except Exception as e:
        conn.rollback()
        logging.exception(f"Error during insertion: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

    finally:
        conn.close()

# endpoint to update an entire student record
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    if student is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    fields = ["name", "course", "email", "phone", "age", "gender", "address"]
    values = [data.get(field) for field in fields]

    if not all(values[:3]):  # Validate name, course, email
        return jsonify({"error": "Missing required fields: name, course, or email"}), 400

    conn.execute('''
        UPDATE students
        SET name=?, course=?, email=?, phone=?, age=?, gender=?, address=?
        WHERE id=?
    ''', (*values, id))
    conn.commit()
    conn.close()
    logging.info(f"PUT /students/{id} - updated successfully")
    return jsonify({"message": "Student record updated successfully!"}), 200


#endpoint to partially update a student record
@app.route('/students/<int:id>', methods=['PATCH'])
def patch_student(id):
    data = request.get_json()
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    if student is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    fields = []
    values = []

    for key, value in data.items():
        if key in student.keys() and key != "id":
            fields.append(f"{key} = ?")
            values.append(value)

    if not fields:
        return jsonify({"error": "No valid fields to update"}), 400

    query = f"UPDATE students SET {', '.join(fields)} WHERE id = ?"
    values.append(id)
    conn.execute(query, values)
    conn.commit()
    conn.close()
    logging.info(f"PATCH /students/{id} - partially updated")
    return jsonify({"message": "Student updated successfully!"}), 200


# to delete a student record
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()
    student = conn.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    if student is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    conn.execute('DELETE FROM students WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    logging.info(f"DELETE /students/{id} - deleted successfully")
    return jsonify({"message": "Student deleted successfully!"}), 200


# to search students by name or course
@app.route('/students/search', methods=['GET'])
def search_students():
    name_query = request.args.get('name', '')
    course_query = request.args.get('course', '')
    conn = get_db_connection()
    students = conn.execute('''
        SELECT * FROM students
        WHERE name LIKE ? OR course LIKE ?
    ''', (f'%{name_query}%', f'%{course_query}%')).fetchall()
    conn.close()
    logging.info(f"GET /students/search - name={name_query}, course={course_query}")
    return jsonify([dict(s) for s in students]), 200


# Head endpoint to check if students resource is available
@app.route('/students', methods=['HEAD'])
def head_students():
    return '', 200

# Options endpoint to list allowed methods

@app.route('/students', methods=['OPTIONS'])
def options_students():
    return jsonify({
        "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
    }), 200



if __name__ == '__main__':
    app.run(debug=True)
