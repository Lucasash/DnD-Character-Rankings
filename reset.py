import psycopg2
try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname="characters",
        user="postgres",
        password="password",
        host="127.0.0.1",
        port="5432" 
    )

   # Create a cursor object to perform database operations
    cur = conn.cursor()

    # Reset all votes in the character_votes table to 0
    cur.execute("UPDATE character_votes SET votes = 0;")

    # Commit the transaction
    conn.commit()

    print("Votes reset successfully!")
except psycopg2.Error as e:
    print("Error:", e)
    conn.rollback()
finally:
    # Close the cursor and the connection
    cur.close()
    conn.close()