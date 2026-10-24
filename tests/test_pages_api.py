"""Isolated tests: no production database or credentials are used."""
import unittest
from datetime import datetime
from app import create_app, db
from app.models import Usuario, Categoria, Producto, MovimientoStock, Venta


class PagesApiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        writer = Usuario(nombre_completo='Prueba', email='test@example.com', has_permisos=True)
        writer.set_password('test-password')
        reader = Usuario(nombre_completo='Lectura', email='read@example.com', has_permisos=False)
        reader.set_password('test-password')
        category = Categoria(nombre='Prueba')
        db.session.add_all([writer, reader, category])
        db.session.flush()
        product = Producto(nombre='Producto prueba', sku='TEST-01', categoria_id=category.id,
                           precio=10, cantidad_stock=5, stock_minimo=2)
        db.session.add(product)
        db.session.commit()
        self.product_id = product.id
        self.category_id = category.id
        self.client = self.app.test_client()
        self.headers = self.auth('test@example.com')

    def auth(self, email):
        result = self.client.post('/api/pages/login', json={'email': email, 'password': 'test-password'})
        self.assertEqual(result.status_code, 200)
        return {'Authorization': 'Bearer ' + result.json['token']}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_auth_and_cors(self):
        self.assertEqual(self.client.get('/api/pages/data').status_code, 401)
        self.assertEqual(self.client.post('/api/pages/login', json={'email': 'missing@example.com', 'password': 'bad'}).status_code, 401)
        result = self.client.get('/api/pages/data', headers={**self.headers, 'Origin': 'https://azaerodiego.github.io'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.headers['Access-Control-Allow-Origin'], 'https://azaerodiego.github.io')
        result = self.client.get('/api/pages/data', headers={**self.headers, 'Origin': 'https://other.example'})
        self.assertNotIn('Access-Control-Allow-Origin', result.headers)
        self.assertEqual(self.client.options('/api/pages/movements', headers={'Origin': 'https://azaerodiego.github.io'}).status_code, 204)

    def test_stock_and_sale_are_atomic(self):
        body = dict(producto_id=self.product_id, tipo='venta', cantidad='3', precio='12')
        self.assertEqual(self.client.post('/api/pages/movements', headers=self.headers, json=body).status_code, 201)
        self.assertEqual(db.session.get(Producto, self.product_id).cantidad_stock, 2)
        self.assertEqual(Venta.query.one().total, 36)
        self.assertEqual(MovimientoStock.query.count(), 1)
        self.assertEqual(self.client.post('/api/pages/movements', headers=self.headers, json=body).status_code, 409)
        self.assertEqual(db.session.get(Producto, self.product_id).cantidad_stock, 2)
        self.assertEqual(Venta.query.count(), 1)
        self.assertEqual(MovimientoStock.query.count(), 1)

    def test_invalid_writes_and_read_only_user(self):
        for amount in ['-1', '1.5', 0, True, 'nan']:
            response = self.client.post('/api/pages/movements', headers=self.headers,
                json=dict(producto_id=self.product_id, tipo='entrada', cantidad=amount))
            self.assertEqual(response.status_code, 400)
        headers = self.auth('read@example.com')
        self.assertEqual(self.client.get('/api/pages/data', headers=headers).status_code, 200)
        self.assertEqual(self.client.post('/api/pages/movements', headers=headers,
            json=dict(producto_id=self.product_id, tipo='entrada', cantidad='1')).status_code, 403)
        self.assertEqual(db.session.get(Producto, self.product_id).cantidad_stock, 5)

    def test_product_and_sku_collision(self):
        body = dict(nombre='Nuevo', sku='NEW-01', categoria_id=self.category_id, precio=8, minimo=3)
        self.assertEqual(self.client.post('/api/pages/products', headers=self.headers, json=body).status_code, 201)
        self.assertEqual(self.client.post('/api/pages/products', headers=self.headers, json=body).status_code, 409)
        self.assertEqual(Producto.query.filter_by(sku='NEW-01').one().cantidad_stock, 0)

    def test_legacy_bridge_and_local_assets(self):
        response = self.client.post('/api/pages/launch', headers=self.headers, json={'target': 'lotes'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/api/pages/launch-session', data={'ticket': response.json['ticket']})
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers['Location'], '/lotes')
        self.assertEqual(self.client.get('/lotes').status_code, 200)
        for path in ('/workspace/', '/workspace/studio.js'):
            with self.client.get(path) as response:
                self.assertEqual(response.status_code, 200)
        response = self.client.post('/api/pages/launch', headers=self.headers, json={'target': 'https://other.example'})
        self.assertEqual(response.status_code, 400)

    def test_sales_chart_includes_records_beyond_history_limit(self):
        user_id = Usuario.query.filter_by(email='test@example.com').one().id
        db.session.add_all([Venta(producto_id=self.product_id, usuario_id=user_id,
            cantidad=1, precio_unitario=10, total=10, fecha=datetime.utcnow()) for _ in range(505)])
        db.session.commit()
        result = self.client.get('/api/pages/data', headers=self.headers)
        self.assertEqual(len(result.json['sales']), 500)
        self.assertEqual(sum(day['total'] for day in result.json['daily_sales']), 5050)


if __name__ == '__main__':
    unittest.main()
