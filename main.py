import psycopg2


def createdb(conn):
    with conn.cursor() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS clients(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(60),
                    last_name VARCHAR(60),
                    email VARCHAR(60)
                    );
                    ''')
        c.execute('''CREATE TABLE IF NOT EXISTS phones(
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER,
                    phone_number VARCHAR(60),
                    FOREIGN KEY(client_id) REFERENCES clients(id)
                    );
                    ''')


def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as c:
        c.execute("INSERT INTO clients (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id",
                  (first_name, last_name, email))
        client_id = c.fetchone()[0]

        if phones:
            for phone in phones:
                add_phone(conn, client_id, phone)

        return client_id


def add_phone(conn, client_id, phone):
    with conn.cursor() as c:
        c.execute("INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)", (client_id, phone))


def update_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    with conn.cursor() as c:
        if first_name:
            c.execute("UPDATE clients SET first_name=%s WHERE id=%s", (first_name, client_id))
        if last_name:
            c.execute("UPDATE clients SET last_name=%s WHERE id=%s", (last_name, client_id))
        if email:
            c.execute("UPDATE clients SET email=%s WHERE id=%s", (email, client_id))

        c.execute("DELETE FROM phones WHERE client_id=%s", (client_id,))

        if phones:
            for phone in phones:
                add_phone(conn, client_id, phone)


def delete_phone(conn, client_id, phone):
    with conn.cursor() as c:
        c.execute("""
                   DELETE FROM phones
                   WHERE client_id=%s AND phone_number=%s
                   RETURNING client_id
                   """, (client_id, phone))
        return c.fetchone()


def delete_client(conn, client_id):
    with conn.cursor() as c:
        c.execute("DELETE FROM phones WHERE client_id=%s", (client_id,))
        c.execute("DELETE FROM clients WHERE id=%s", (client_id,))


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as c:
        query = "SELECT * FROM clients LEFT JOIN phones ON clients.id = phones.client_id WHERE True"
        params = []

        if first_name:
            query += " AND first_name = %s"
            params.append(first_name)
        if last_name:
            query += " AND last_name = %s"
            params.append(last_name)
        if email:
            query += " AND email = %s"
            params.append(email)
        if phone:
            query += " AND phone_number = %s"
            params.append(phone)

        c.execute(query, params)
        rows = c.fetchall()

        return rows


if __name__ == '__main__':
    with psycopg2.connect(database='netology_db', user='postgres', password='Zpro100flower') as conn:
        createdb(conn)
        client_id = add_client(conn, 'Starichikhin', 'Maxim', 'maks.mayer.ru@outlook.com')
        add_phone(conn, client_id, '88005553535')
        print(find_client(conn, first_name='Maxim', last_name='Starichikhin'))
