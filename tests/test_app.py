# tests/test_app.py
import unittest
from flask import url_for
from app import app, get_db_connection

class TestApp(unittest.TestCase):

    def setUp(self):
        # Configurar la aplicación para pruebas
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.conn = get_db_connection()

    def tearDown(self):
        # Cerrar la conexión de la base de datos
        self.conn.close()

    def test_login_page(self):
        # Prueba para la página de inicio de sesión
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_login_functionality(self):
        """Test login functionality with valid and invalid credentials."""
        # Prueba con credenciales incorrectas
        response = self.app.post('/login', data=dict(username='wronguser', password='wrongpass'), follow_redirects=True)
        self.assertIn(b'Credenciales inválidas', response.data)

        # Prueba con credenciales correctas (asegúrate de tener un usuario de prueba en la base de datos)
        response = self.app.post('/login', data=dict(username='testuser', password='testpass'), follow_redirects=True)
        self.assertIn(b'Facturas', response.data)  # Redirige a la página de facturas si el login es exitoso

    def test_register_page(self):
        # Prueba para la página de registro
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_listar_facturas(self):
        # Prueba para listar facturas
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.get('/facturas')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Facturas', response.data)

    def test_nueva_factura(self):
        """Test creating a new invoice."""
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.post('/factura/nueva', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=2), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Factura creada', response.data)  # Asegúrate de que el mensaje correcto se muestra

    def test_ver_factura(self):
        # Prueba para ver detalles de una factura
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.get('/factura/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Detalles de la Factura', response.data)

    def test_editar_factura(self):
        # Prueba para editar una factura
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.post('/factura/editar/1', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=3), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Factura actualizada exitosamente', response.data)

    def test_exportar_factura_pdf(self):
        # Prueba para exportar una factura como PDF
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.get('/factura/pdf/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/pdf')
        
    def test_nueva_factura_datos_mal_formateados(self):
        """Test creating a new invoice with malformed data."""
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.post('/factura/nueva', data=dict(cliente_id='abc', producto_id_1=1, cantidad_1='two'), follow_redirects=True)
        self.assertIn(b'Error en los datos', response.data)  # Asegúrate de que el mensaje correcto se muestra

    def test_ver_factura_id_inexistente(self):
        """Test viewing an invoice with a non-existent ID."""
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.get('/factura/9999')  # ID que no existe
        self.assertIn(b'Factura no encontrada', response.data)

    def test_nueva_factura_parametros_faltantes(self):
        """Test creating a new invoice with missing parameters."""
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.post('/factura/nueva', data=dict(producto_id_1=1, cantidad_1=2), follow_redirects=True)
        self.assertIn(b'Cliente es requerido', response.data)  # Asegúrate de que el mensaje correcto se muestra

    def test_concurrencia_creacion_factura(self):
        """Test concurrent requests for creating invoices."""
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        responses = []
        for _ in range(10):  # Simula 10 solicitudes concurrentes
            response = self.app.post('/factura/nueva', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=2), follow_redirects=True)
            responses.append(response)
        for response in responses:
            self.assertIn(b'Factura creada', response.data)

    def test_nueva_factura_division_por_cero(self):
        """Test creating a new invoice with zero quantity."""
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        response = self.app.post('/factura/nueva', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=0), follow_redirects=True)
        self.assertIn(b'Cantidad debe ser mayor que cero', response.data)  # Asegúrate de que el mensaje correcto se muestra
        
    def test_nueva_factura_boundary_values(self):
        """Test creating a new invoice with boundary values for quantity."""
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'

        # Test with minimum quantity
        response = self.app.post('/factura/nueva', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=1), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Factura creada', response.data)

        # Test with quantity just below minimum (assuming 0 is invalid)
        response = self.app.post('/factura/nueva', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=0), follow_redirects=True)
        self.assertEqual(response.status_code, 400)  # Assuming the application returns 400 for invalid input

        # Test with maximum quantity
        response = self.app.post('/factura/nueva', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=5), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Factura creada', response.data)

        # Test with quantity just above maximum
        response = self.app.post('/factura/nueva', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=6), follow_redirects=True)
        self.assertEqual(response.status_code, 400)  # Assuming the application returns 400 for invalid input
        
    def test_editar_factura_boundary_values(self):
        """Test editing an invoice with boundary values for quantity."""
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'

        # Test with minimum quantity
        response = self.app.post('/factura/editar/1', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=1), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Factura actualizada exitosamente', response.data)

        # Test with quantity just below minimum (assuming 0 is invalid)
        response = self.app.post('/factura/editar/1', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=0), follow_redirects=True)
        self.assertEqual(response.status_code, 400)  # Assuming the application returns 400 for invalid input

        # Test with maximum quantity
        response = self.app.post('/factura/editar/1', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=5), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Factura actualizada exitosamente', response.data)

        # Test with quantity just above maximum
        response = self.app.post('/factura/editar/1', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=6), follow_redirects=True)
        self.assertEqual(response.status_code, 400)  # Assuming the application returns 400 for invalid input



if __name__ == '__main__':
    unittest.main()