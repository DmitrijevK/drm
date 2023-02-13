import os
import hashlib
import random
import pymysql.cursors
import lupa

DB_HOST = "localhost"
DB_USER = "root"

def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return file.read()
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def write_file(file_path, content):
    try:
        with open(file_path, "w") as file:
            file.write(content)
    except Exception as e:
        print(f"An error occurred while writing the file: {e}")

def obfuscate_lua(file_content):
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)
    obfuscated_code = lua.execute(f"return require('obfuscate')({file_content})")
    return obfuscated_code

def generate_hash_key():
    # Generate a random hash key
    return hashlib.sha256(str(random.getrandbits(256)).encode("utf-8")).hexdigest()

def generate_deobfuscation_key():
    # Generate a random deobfuscation key
    return str(random.getrandbits(256))

def main():
    file_path = input("Enter the path of the Lua file: ")
    file_name = os.path.basename(file_path)
    file_content = read_file(file_path)

    if file_content is not None:
        # Obfuscate the Lua file
        obfuscated_file_content = obfuscate_lua(file_content)
        obfuscated_file_path = os.path.join(os.path.dirname(file_path), "obfuscated_" + file_name)
        write_file(obfuscated_file_path, obfuscated_file_content)

        # Generate the hash key and deobfuscation key
        hash_key = generate_hash_key()
        deobfuscation_key = generate_deobfuscation_key()

        # Write the hash key and deobfuscation key to a text file
        key_file_path = os.path.join(os.path.dirname(file_path), "key.txt")
        write_file(key_file_path, "Hash Key: " + hash_key + "\nDeobfuscation Key: " + deobfuscation_key)

        # Connect to the database
        mydb = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="gmlua"
        )
        try:
            with mydb.cursor() as cursor:
                # Check if the hash key already exists in the database
                sql = "SELECT * FROM glua WHERE `hash_key` = %s"
                cursor.execute(sql, (hash_key,))
                result = cursor.fetchone()
                while result is not None:
                    hash_key = generate_hash_key()
                    sql = "SELECT * FROM glua WHERE `hash_key` = %s"
                    cursor.execute(sql, (hash_key,))
                    result = cursor.fetchone()

                # Insert the hash key and deobfuscation key into the database
                sql = "INSERT INTO glua (license_key, hash_key, ip, status) VALUES (%s,%s,%s,%s,)"
                cursor.execute(sql, (deobfuscation_key, hash_key, "", 0))
        except Exception as e:
            print("An error occurred while connecting to the database:", e)
        finally:
            mydb.commit()
            mydb.close()
