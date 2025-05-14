import unittest
from app import app, get_db_connection

import unittest
from app import app, get_db_connection

class TestSecurity(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_access_protected_route_without_login(self):
        response = self.app.get('/facturas', follow_redirects=True)
        self.assertIn(b'Login', response.data, "Expected redirect to login page when accessing protected route without authentication.")

if __name__ == '__main__':
    unittest.main()


class TestCSRFProtection(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_csrf_protection_on_post_request(self):
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        
        response = self.app.post('/factura/nueva', data=dict(cliente_id=1, producto_id_1=1, cantidad_1=2), follow_redirects=True)
        self.assertNotIn(b'Factura creada', response.data, "Expected CSRF protection to prevent form submission without CSRF token.")

if __name__ == '__main__':
    unittest.main()

class TestDataValidation(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_invalid_data_submission(self):
        with self.app.session_transaction() as session:
            session['usuario'] = 'TEST_USER'
        
        response = self.app.post('/factura/nueva', data=dict(cliente_id='', producto_id_1='invalid', cantidad_1='-1'), follow_redirects=True)
        self.assertIn(b'Error en los datos', response.data, "Expected error message when submitting invalid data.")

if __name__ == '__main__':
    unittest.main()
