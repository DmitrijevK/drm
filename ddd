import platform
import socket
import pymysql.cursors
import time

# Connect to the database
mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="gmlua"
)
mycursor = mydb.cursor()

# Create table for client information
table_sql = "CREATE TABLE IF NOT EXISTS glua (license_Key VARCHAR(255), Ipaddress VARCHAR(255), hash_key VARCHAR(255), Status INT(1), TimeStamp DATETIME DEFAULT CURRENT_TIMESTAMP)"
mycursor.execute(table_sql)

# Set up the server socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostbyname(socket.gethostname())
port = 5000
sock.bind((host, port))
sock.listen()
print("Server started on %s:%s" % (host, port))

# Keep track of active clients and their last request times
active_clients = {}

while True:
    # Accept a new connection
    client, address = sock.accept()
    print("Received a new connection from %s:%s" % (address[0], address[1]))

    # Check if the client's key is in the database
    key = client.recv(1024).decode()
    mycursor.execute("SELECT * FROM glua WHERE license_Key = %s", (key, ))
    result = mycursor.fetchone()

    if result:
        # Check if the client's IP is in the database
        client_ip = address[0]
        mycursor.execute("SELECT * FROM glua WHERE license_Key = %s AND Ipaddress = %s", (key, client_ip))
        ip_result = mycursor.fetchone()

        if not ip_result:
            # If the client's IP is not in the database, add it
            mycursor.execute("UPDATE glua SET Ipaddress = %s, Status = 1 WHERE license_Key = %s", (client_ip, key))
            mydb.commit()

        # Update the client's last request time
        active_clients[client_ip] = time.time()
        client.send(b"successfull")

    else:
        # If the key is not in the database, send an error message
        client.send(b"error")

    # Check if any clients have timed out
    for ip, last_request in active_clients.items():
        if time.time() - last_request > 60:  # Timeout after 60 seconds
            mycursor.execute("UPDATE glua SET Status = 0, Ipaddress = NULL WHERE Ipaddress = %s", (ip, ))
            mydb.commit()
            del active_clients[ip]

# Close the connections
client.close()
mycursor.close()
mydb.close()
