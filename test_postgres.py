import psycopg2
import io
import numpy as np


def create_connection():
    conn = psycopg2.connect(
        dbname="test",
        user="postgres",
        password="password",
        host="localhost",
        port="5432",
    )
    curr = conn.cursor()
    return conn, curr


def create_table():
    try:
        conn, curr = create_connection()

        try:
            curr.execute(
                "CREATE TABLE IF NOT EXISTS cartoon(cartoonID INTEGER, name TEXT, cartoonImg BYTEA)"
            )
        except (Exception, psycopg2.Error) as error:
            print(error)
        finally:
            conn.commit()
            conn.close()
    finally:
        pass


x = np.random.randn(56000000).reshape(8000, 7000)
x = x / 10
x = x + 0.5
x[x < 0] = 0
x[x > 1] = 1

x = x * (1 << 12)
x = x.astype(np.uint16)

memfile = io.BytesIO()
np.save(memfile, x)
image = memfile.getvalue()


def write_blob(cartoonID, file_path, name):
    try:
        # drawing = open(file_path, "rb").read()
        drawing = b"hello world"
        drawing = image
        data = psycopg2.Binary(drawing)
        conn, cursor = create_connection()
        try:
            cursor.execute(
                "INSERT INTO cartoon (cartoonID, name, cartoonImg) "
                + "VALUES(%s, %s, %s)",
                (cartoonID, name, data),
            )
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            conn.close()
    finally:
        pass


create_table()
write_blob(1, "", "Casper")
write_blob(2, "", "Casper")
write_blob(3, "", "Casper")
write_blob(4, "", "Casper")
write_blob(5, "", "Casper")
