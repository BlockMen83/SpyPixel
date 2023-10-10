import uuid
import sqlite3
from datetime import datetime
from flask import Flask, request, render_template, send_file, redirect, url_for

app = Flask(__name__)

def generate_unique_id():
    return str(uuid.uuid4())

def insert_pixel_info(pixel_id, recipient):
    access_time = datetime.now()
    conn = sqlite3.connect('pixels.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pixels (id, recipient, access_time, counter) VALUES (?, ?, ?, ?)",
                   (pixel_id, recipient, access_time, 0))
    conn.commit()
    conn.close()

@app.route("/pixel.png")
def tracking_pixel():
    pixel_id = request.args.get('id')
    ip_address = request.remote_addr
    access_time = datetime.now()
    conn = sqlite3.connect('pixels.db')
    cursor = conn.cursor()
    
    # Check if the pixel_id exists in the database
    cursor.execute("SELECT counter FROM pixels WHERE id = ?", (pixel_id,))
    result = cursor.fetchone()
    
    if result:
        # If the pixel_id exists, increment the access count
        cursor.execute("UPDATE pixels SET access_time = ?, counter = counter + 1 WHERE id = ?", (access_time, pixel_id))
    else:
        # If the pixel_id does not exist, insert it into the database
        cursor.execute("INSERT INTO pixels (id, access_time, counter) VALUES (?, ?, 1)", (pixel_id, access_time))
    
    conn.commit()
    conn.close()
    return send_file("pixel.png", mimetype='image/png')

@app.route("/", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        recipient = request.form.get("recipient")
        pixel_id = generate_unique_id()
        insert_pixel_info(pixel_id, recipient)
        pixel_url = f"http://localhost:5000/pixel.png?id={pixel_id}"
        return redirect(url_for('dashboard') + f"?pixel_url={pixel_url}")

    conn = sqlite3.connect('pixels.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, recipient, access_time, counter FROM pixels")
    all_data = cursor.fetchall()
    conn.close()

    email_data = {}
    for data in all_data:
        pixel_id, recipient, access_time_str, counter = data
        access_time = datetime.strptime(access_time_str, "%Y-%m-%d %H:%M:%S.%f")
        formatted_access_time = access_time.strftime('%d/%m/%Y %H:%M:%S')
        
        if pixel_id not in email_data:
            email_data[pixel_id] = []
        email_data[pixel_id].append((recipient, formatted_access_time, counter))

    pixel_url = request.args.get("pixel_url", None)
    return render_template("dashboard.html", email_data=email_data, pixel_url=pixel_url)

@app.route("/delete_pixel/<pixel_id>", methods=["POST"])
def delete_pixel(pixel_id):
    conn = sqlite3.connect('pixels.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pixels WHERE id = ?", (pixel_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
