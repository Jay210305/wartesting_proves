import unittest
import psycopg2
import os
from init_db import create_tables, DB_CONFIG

class TestInitDB(unittest.TestCase):

    def setUp(self):
        # Configurar la conexión a la base de datos de pruebas
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()

    def tearDown(self):
        # Cerrar la conexión y limpiar la base de datos
        self.cur.execute("DROP TABLE IF EXISTS factura_items CASCADE")
        self.cur.execute("DROP TABLE IF EXISTS facturas CASCADE")
        self.cur.execute("DROP TABLE IF EXISTS productos CASCADE")
        self.cur.execute("DROP TABLE IF EXISTS clientes CASCADE")
        self.cur.execute("DROP SEQUENCE IF EXISTS factura_numero_seq")
        self.conn.commit()
        self.cur.close()
        self.conn.close()

    def test_create_tables(self):
        """Test the creation of tables in the database."""
        # Ejecutar la función para crear tablas
        create_tables()

        # Verificar que las tablas se han creado
        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = self.cur.fetchall()
        expected_tables = {'clientes', 'productos', 'facturas', 'factura_items'}
        created_tables = {table[0] for table in tables}

        self.assertTrue(expected_tables.issubset(created_tables), f"Expected tables {expected_tables}, but got {created_tables}")

    def test_insert_test_data(self):
        # Ejecutar la función para crear tablas (incluye inserción de datos)
        create_tables()

        # Verificar que los datos de prueba se han insertado
        self.cur.execute("SELECT COUNT(*) FROM clientes;")
        clientes_count = self.cur.fetchone()[0]
        self.assertGreater(clientes_count, 0, "Expected clients to be inserted, but found none.")

        self.cur.execute("SELECT COUNT(*) FROM productos;")
        productos_count = self.cur.fetchone()[0]
        self.assertGreater(productos_count, 0, "Expected products to be inserted, but found none.")


    def test_factura_numero_seq(self):
        """Test the creation of the invoice number sequence."""
        # Ejecutar la función para crear tablas
        create_tables()

        # Verificar que la secuencia se ha creado
        self.cur.execute("SELECT * FROM pg_sequences WHERE sequencename='factura_numero_seq';")
        sequence = self.cur.fetchone()
        self.assertIsNotNone(sequence, "Expected sequence 'factura_numero_seq' to be created, but found none.")
        
    def test_insert_duplicate_client_email(self):
        """Test insertion of duplicate client email."""
        create_tables()  # Asegúrate de que las tablas están creadas

        # Insertar un cliente con un correo electrónico específico
        self.cur.execute(
            "INSERT INTO clientes (nombre, direccion, telefono, email) VALUES (%s, %s, %s, %s);",
            ("Test Client", "Test Address", "123456789", "duplicate@example.com")
        )
        self.conn.commit()

        # Intentar insertar otro cliente con el mismo correo electrónico
        with self.assertRaises(psycopg2.IntegrityError):
            self.cur.execute(
                "INSERT INTO clientes (nombre, direccion, telefono, email) VALUES (%s, %s, %s, %s);",
                ("Another Client", "Another Address", "987654321", "duplicate@example.com")
            )
            self.conn.commit()
            
    def test_insert_duplicate_product_name(self):
        """Test insertion of duplicate product name."""
        create_tables()  # Asegúrate de que las tablas están creadas

        # Insertar un producto con un nombre específico
        self.cur.execute(
            "INSERT INTO productos (nombre, descripcion, precio) VALUES (%s, %s, %s);",
            ("Unique Product", "Description", 100.00)
        )
        self.conn.commit()

        # Intentar insertar otro producto con el mismo nombre
        with self.assertRaises(psycopg2.IntegrityError):
            self.cur.execute(
                "INSERT INTO productos (nombre, descripcion, precio) VALUES (%s, %s, %s);",
                ("Unique Product", "Another Description", 150.00)
            )
            self.conn.commit()
            
    def test_insert_null_values(self):
        """Test insertion of null values in mandatory fields."""
        create_tables()  # Asegúrate de que las tablas están creadas

        # Intentar insertar un cliente con un nombre nulo
        with self.assertRaises(psycopg2.IntegrityError):
            self.cur.execute(
                "INSERT INTO clientes (nombre, direccion, telefono, email) VALUES (%s, %s, %s, %s);",
                (None, "Address", "123456789", "null@example.com")
            )
            self.conn.commit()

        # Intentar insertar un producto con un precio nulo
        with self.assertRaises(psycopg2.IntegrityError):
            self.cur.execute(
                "INSERT INTO productos (nombre, descripcion, precio) VALUES (%s, %s, %s);",
                ("Product", "Description", None)
            )
            self.conn.commit()

    def test_insert_client_name_boundary(self):
        """Test insertion of client names at boundary values."""
        create_tables()  # Asegúrate de que las tablas están creadas

        # Nombre con 1 carácter
        self.cur.execute(
            "INSERT INTO clientes (nombre, direccion, telefono, email) VALUES (%s, %s, %s, %s);",
            ("A", "Address", "123456789", "onechar@example.com")
        )
        self.conn.commit()

        # Verificar que el cliente se haya insertado
        self.cur.execute("SELECT COUNT(*) FROM clientes WHERE email = 'onechar@example.com';")
        count = self.cur.fetchone()[0]
        self.assertEqual(count, 1, "Expected client with 1 character name to be inserted.")

        # Nombre con 100 caracteres
        long_name = "A" * 100
        self.cur.execute(
            "INSERT INTO clientes (nombre, direccion, telefono, email) VALUES (%s, %s, %s, %s);",
            (long_name, "Address", "123456789", "longname@example.com")
        )
        self.conn.commit()

        # Verificar que el cliente se haya insertado
        self.cur.execute("SELECT COUNT(*) FROM clientes WHERE email = 'longname@example.com';")
        count = self.cur.fetchone()[0]
        self.assertEqual(count, 1, "Expected client with 100 character name to be inserted.")

    def test_insert_product_price_boundary(self):
        """Test insertion of product prices at boundary values."""
        create_tables()  # Asegúrate de que las tablas están creadas

        # Precio mínimo permitido
        self.cur.execute(
            "INSERT INTO productos (nombre, descripcion, precio) VALUES (%s, %s, %s);",
            ("Cheap Product", "Description", 0.01)
        )
        self.conn.commit()

        # Verificar que el producto se haya insertado
        self.cur.execute("SELECT COUNT(*) FROM productos WHERE nombre = 'Cheap Product';")
        count = self.cur.fetchone()[0]
        self.assertEqual(count, 1, "Expected product with minimum price to be inserted.")

        # Precio máximo razonable
        self.cur.execute(
            "INSERT INTO productos (nombre, descripcion, precio) VALUES (%s, %s, %s);",
            ("Expensive Product", "Description", 9999.99)
        )
        self.conn.commit()

        # Verificar que el producto se haya insertado
        self.cur.execute("SELECT COUNT(*) FROM productos WHERE nombre = 'Expensive Product';")
        count = self.cur.fetchone()[0]
        self.assertEqual(count, 1, "Expected product with maximum price to be inserted.")



if __name__ == '__main__':
    unittest.main()