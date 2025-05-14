from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import unittest
import time

class TestIntegration(unittest.TestCase):
    def setUp(self):
        # Configurar el navegador
        self.driver = webdriver.Chrome()  # Asegúrate de tener chromedriver en tu PATH
        self.driver.get('http://localhost:5000/login')  # URL de la aplicación

    def tearDown(self):
        # Cerrar el navegador
        self.driver.quit()

    def test_register(self):
        """Test user registration functionality."""
        driver = self.driver
        driver.get('http://localhost:5000/register')

        # Encontrar los elementos de entrada y botón
        nombre_input = driver.find_element(By.ID, 'nombre')
        email_input = driver.find_element(By.ID, 'email')
        password_input = driver.find_element(By.ID, 'password')
        key_secret_input = driver.find_element(By.ID, 'key_secret')
        submit_button = driver.find_element(By.TAG_NAME, 'button')

        # Ingresar datos de prueba
        nombre_input.send_keys('newuser')
        email_input.send_keys('newuser@example.com')
        password_input.send_keys('newpassword')
        key_secret_input.send_keys('correct_secret_key')  # Reemplaza con la clave secreta correcta

        # Hacer clic en el botón de enviar
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que el usuario se haya registrado correctamente
        self.assertIn('Iniciar Sesión', driver.page_source)

    def test_login(self):
        """Test login functionality."""
        driver = self.driver

        # Encontrar los elementos de entrada y botón
        username_input = driver.find_element(By.ID, 'username')
        password_input = driver.find_element(By.ID, 'password')
        submit_button = driver.find_element(By.TAG_NAME, 'button')

        # Ingresar datos de prueba
        username_input.send_keys('testuser')
        password_input.send_keys('testpass')

        # Hacer clic en el botón de enviar
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que el usuario haya iniciado sesión correctamente
        self.assertIn('Facturas', driver.page_source)

    def test_create_invoice(self):
        """Test creating a new invoice."""
        driver = self.driver
        driver.get('http://localhost:5000/factura/nueva')

        # Seleccionar cliente
        cliente_select = Select(driver.find_element(By.ID, 'cliente_id'))
        cliente_select.select_by_visible_text('Juan Pérez')  # Reemplaza con un cliente existente

        # Seleccionar producto y cantidad
        producto_select = Select(driver.find_element(By.ID, 'producto_id_1'))
        producto_select.select_by_visible_text('Laptop HP')  # Reemplaza con un producto existente
        cantidad_input = driver.find_element(By.ID, 'cantidad_1')
        cantidad_input.send_keys('2')

        # Hacer clic en el botón de guardar
        submit_button = driver.find_element(By.CLASS_NAME, 'btn')
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que la factura se haya creado correctamente
        self.assertIn('Factura creada', driver.page_source)

    def test_edit_invoice(self):
        """Test editing an existing invoice."""
        driver = self.driver
        driver.get('http://localhost:5000/factura/editar/1')  # Reemplaza con un ID de factura existente

        # Cambiar cliente
        cliente_select = Select(driver.find_element(By.ID, 'cliente_id'))
        cliente_select.select_by_visible_text('María López')  # Reemplaza con un cliente existente

        # Cambiar producto y cantidad
        producto_select = Select(driver.find_element(By.ID, 'producto_id_1'))
        producto_select.select_by_visible_text('Monitor Samsung')  # Reemplaza con un producto existente
        cantidad_input = driver.find_element(By.ID, 'cantidad_1')
        cantidad_input.clear()
        cantidad_input.send_keys('3')

        # Hacer clic en el botón de guardar
        submit_button = driver.find_element(By.CLASS_NAME, 'btn')
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que la factura se haya editado correctamente
        self.assertIn('Factura actualizada exitosamente', driver.page_source)

    def test_export_invoice_pdf(self):
        """Test exporting an invoice to PDF."""
        driver = self.driver
        driver.get('http://localhost:5000/factura/pdf/1')  # Reemplaza con un ID de factura existente

        # Esperar a que se genere el PDF
        time.sleep(2)

        # Verificar que el PDF se haya generado correctamente
        self.assertIn('application/pdf', driver.page_source)
        
    def test_search_invoice(self):
        """Test searching for an invoice."""
        driver = self.driver
        driver.get('http://localhost:5000/facturas')

        # Seleccionar criterio de búsqueda
        criterio_select = Select(driver.find_element(By.ID, 'criterio'))
        criterio_select.select_by_visible_text('Número de Factura')

        # Ingresar valor de búsqueda
        valor_input = driver.find_element(By.ID, 'valor')
        valor_input.send_keys('FACT-001')  # Reemplaza con un número de factura existente

        # Hacer clic en el botón de buscar
        submit_button = driver.find_element(By.CLASS_NAME, 'btn')
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que la factura se haya encontrado correctamente
        self.assertIn('FACT-001', driver.page_source)

        def test_register_empty_fields(self):
        """Test registration with empty fields."""
        driver = self.driver
        driver.get('http://localhost:5000/register')

        # Encontrar los elementos de entrada y botón
        submit_button = driver.find_element(By.TAG_NAME, 'button')

        # Dejar todos los campos vacíos y enviar el formulario
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que se muestre un mensaje de error
        self.assertIn('Por favor, complete todos los campos', driver.page_source)

    def test_register_special_characters(self):
        """Test registration with special characters."""
        driver = self.driver
        driver.get('http://localhost:5000/register')

        # Encontrar los elementos de entrada y botón
        nombre_input = driver.find_element(By.ID, 'nombre')
        email_input = driver.find_element(By.ID, 'email')
        password_input = driver.find_element(By.ID, 'password')
        key_secret_input = driver.find_element(By.ID, 'key_secret')
        submit_button = driver.find_element(By.TAG_NAME, 'button')

        # Ingresar caracteres especiales
        nombre_input.send_keys('!@#$%^&*()')
        email_input.send_keys('invalid_email')
        password_input.send_keys('123456')
        key_secret_input.send_keys('correct_secret_key')  # Reemplaza con la clave secreta correcta

        # Hacer clic en el botón de enviar
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que se muestre un mensaje de error
        self.assertIn('Por favor, ingrese un nombre válido', driver.page_source)

    def test_login_empty_fields(self):
        """Test login with empty fields."""
        driver = self.driver

        # Encontrar los elementos de entrada y botón
        submit_button = driver.find_element(By.TAG_NAME, 'button')

        # Dejar todos los campos vacíos y enviar el formulario
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que se muestre un mensaje de error
        self.assertIn('Por favor, ingrese su nombre de usuario y contraseña', driver.page_source)

    def test_create_invoice_empty_fields(self):
        """Test creating an invoice with empty fields."""
        driver = self.driver
        driver.get('http://localhost:5000/factura/nueva')

        # Hacer clic en el botón de guardar sin seleccionar cliente ni productos
        submit_button = driver.find_element(By.CLASS_NAME, 'btn')
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que se muestre un mensaje de error
        self.assertIn('Por favor, seleccione un cliente y al menos un producto', driver.page_source)

    def test_edit_invoice_invalid_data(self):
        """Test editing an invoice with invalid data."""
        driver = self.driver
        driver.get('http://localhost:5000/factura/editar/1')  # Reemplaza con un ID de factura existente

        # Cambiar cantidad a un valor no numérico
        cantidad_input = driver.find_element(By.ID, 'cantidad_1')
        cantidad_input.clear()
        cantidad_input.send_keys('abc')

        # Hacer clic en el botón de guardar
        submit_button = driver.find_element(By.CLASS_NAME, 'btn')
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que se muestre un mensaje de error
        self.assertIn('Por favor, ingrese una cantidad válida', driver.page_source)

    def test_search_invoice_invalid_data(self):
        """Test searching for an invoice with invalid data."""
        driver = self.driver
        driver.get('http://localhost:5000/facturas')

        # Ingresar valor de búsqueda no numérico para el número de factura
        valor_input = driver.find_element(By.ID, 'valor')
        valor_input.send_keys('!@#$%')

        # Hacer clic en el botón de buscar
        submit_button = driver.find_element(By.CLASS_NAME, 'btn')
        submit_button.click()

        # Esperar a que se cargue la página
        time.sleep(2)

        # Verificar que se muestre un mensaje de error
        self.assertIn('Por favor, ingrese un número de factura válido', driver.page_source)

if __name__ == '__main__':
    unittest.main()
