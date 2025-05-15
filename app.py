from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coffeecorne.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Готовится')
    created_at = db.Column(db.DateTime, default=datetime.now)
    completed_at = db.Column(db.DateTime)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    employee = db.relationship('Employee', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy='joined')

    @property
    def total_price(self):
        return sum(item.menu_item.price * item.quantity for item in self.items)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    quantity = db.Column(db.Integer, default=1)
    menu_item = db.relationship('MenuItem', lazy='joined')

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'image': f"static/{self.image}" if self.image else None
        }


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def verify_password(self, password):
        return self.password == password

with app.app_context():
    db.create_all()

    if not MenuItem.query.first():
        menu_items = [
            MenuItem(name="Капучино", price=200, category="кофе", image="images/capichino.png"),
            MenuItem(name="Американо", price=200, category="кофе", image="images/amerikano.png"),
            MenuItem(name="Латте", price=300, category="кофе", image="images/latte.png"),
            MenuItem(name="Эспрессо", price=200, category="кофе", image="images/espresso.png"),
            MenuItem(name="Раф лавандовый", price=350, category="кофе", image="images/raf-lavand.png"),
            MenuItem(name="Раф с соленой карамелью", price=350, category="кофе", image="images/raf-caramel.png"),
            MenuItem(name="Флет уайт", price=350, category="кофе", image="images/flet.png"),
            MenuItem(name="Айс латте", price=300, category="кофе", image="images/ice-latte.png"),
            MenuItem(name="Айс раф лавандовый", price=350, category="кофе", image="images/raf-lavand.png"),
            MenuItem(name="Айс раф с соленой карамелью", price=350, category="кофе",
                     image="images/cold-raf-caramel.png"),
            MenuItem(name="Чай черный", price=200, category="чай", image="images/black-tea.png"),
            MenuItem(name="Чай зеленый", price=200, category="чай", image="images/tea-green.png"),
            MenuItem(name="Чай облепиховый", price=250, category="чай", image="images/tea-obl.png"),
            MenuItem(name="Чай ягодный", price=250, category="чай", image="images/tea-berry.png"),
            MenuItem(name="Матча", price=300, category="чай", image="images/matcha.png"),
            MenuItem(name="Какао", price=200, category="сезонные напитки", image="images/cacao.png"),
            MenuItem(name="Пряный латте", price=350, category="сезонные напитки", image="images/latte-pr.png"),
            MenuItem(name="Раф фисташковый", price=350, category="сезонные напитки", image="images/raf-fist.png"),
            MenuItem(name="Медовик", price=300, category="десерты", image="images/med.png"),
            MenuItem(name="Тирамису", price=300, category="десерты", image="images/tiramisu.png"),
            MenuItem(name="Наполеон", price=300, category="десерты", image="images/napoleon.png"),
            MenuItem(name="Эклер", price=300, category="выпечка", image="images/eclair.png"),
            MenuItem(name="Шоколадное печенье", price=200, category="выпечка", image="images/coockies.png"),
            MenuItem(name="Круассан миндальный", price=350, category="выпечка",
                     image="images/croissant-almond.png"),
            MenuItem(name="Круассан шоколадный", price=350, category="выпечка", image="images/cr-ch.png"),
            MenuItem(name="Фисташковый рулет", price=350, category="выпечка", image="images/fist-rul.png"),
            MenuItem(name="Творожное кольцо", price=250, category="выпечка", image="images/tw.png")
        ]
        db.session.bulk_save_objects(menu_items)

        employees = [
            Employee(login="IvanIvanov123", password="II1v2a3n", name="Иван"),
            Employee(login="MariaPetrova456", password="PM4a5r6y", name="Мария"),
            Employee(login="LizzyVelichko789", password="VL7i8z9y", name="Елизавета"),
            Employee(login="SvetlanaZakharova101112", password="SZ10v11e12t", name="Светлана"),
            Employee(login="VictorPeshkov131415", password="VP13i14c15t", name="Виктор")
        ]
        db.session.bulk_save_objects(employees)
        db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def get_menu():
    category = request.args.get('category', 'Все')
    if category == 'Все':
        items = MenuItem.query.all()
    else:
        items = MenuItem.query.filter_by(category=category).all()
    return jsonify([item.to_dict() for item in items])

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        data = request.get_json()
        cart = data.get('cart', [])
        table_number = data.get('table_number')

        if not cart or not table_number:
            return jsonify({'error': 'Необходимо указать номер стола и выбрать товары'}), 400

        employee = db.session.query(Employee).outerjoin(Order, (Employee.id == Order.employee_id) &
                                                        (Order.status != 'Завершен')).group_by(Employee.id).order_by(
            db.func.count(Order.id)).first()

        if not employee:
            return jsonify({'error': 'Нет доступных официантов'}), 400

        new_order = Order(
            table_number=table_number,
            employee_id=employee.id,
            status='Готовится'
        )
        db.session.add(new_order)
        db.session.commit()

        for item in cart:
            menu_item = MenuItem.query.get(item['id'])
            if menu_item:
                order_item = OrderItem(
                    order_id=new_order.id,
                    menu_item_id=menu_item.id,
                    quantity=item['quantity']
                )
                db.session.add(order_item)

        db.session.commit()

        return jsonify({
            'order_id': new_order.id,
            'redirect': url_for('order_status', order_id=new_order.id)
        })

    return render_template('order.html')


@app.route('/api/orders')
def get_orders():
    if 'employee_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    orders = Order.query.options(
        db.joinedload(Order.items).joinedload(OrderItem.menu_item),
        db.joinedload(Order.employee)
    ).filter(Order.status != 'Завершен').all()

    orders_data = []
    for order in orders:
        items = []
        total = 0
        for item in order.items:
            items.append(f"{item.menu_item.name} × {item.quantity}")
            total += item.menu_item.price * item.quantity

        orders_data.append({
            'id': order.id,
            'table': order.table_number,
            'items': items,
            'status': order.status,
            'total': total,
            'created_at': order.created_at.strftime('%H:%M'),
            'employee': order.employee.name
        })

    return jsonify(orders_data)

@app.route('/api/menu')
def get_full_menu():
    if 'employee_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    items = MenuItem.query.all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'price': item.price,
        'category': item.category,
        'image': url_for('static', filename=item.image) if item.image else None
    } for item in items])

@app.route('/order/<int:order_id>')
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('order_status.html', order=order)


@app.route('/api/orders/<int:order_id>', methods=['PUT', 'DELETE'])
def manage_order(order_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    order = Order.query.get_or_404(order_id)

    if request.method == 'PUT':
        new_status = request.json.get('status')
        if new_status in ['Готовится', 'Готов', 'Завершен']:
            order.status = new_status
            if new_status == 'Завершен':
                order.completed_at = datetime.now()
            db.session.commit()
            return jsonify({'status': 'success'})
        return jsonify({'error': 'Invalid status'}), 400

    elif request.method == 'DELETE':
        db.session.delete(order)
        db.session.commit()
        return jsonify({'status': 'success'})


@app.route('/api/menu/<int:item_id>', methods=['GET'])
def get_menu_item(item_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    item = MenuItem.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@app.route('/api/menu', methods=['POST'])
def manage_menu():
    if 'employee_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    if 'id' in request.form:
        item = MenuItem.query.get(request.form['id'])
        if item:
            item.name = request.form.get('name', item.name)
            item.price = float(request.form.get('price', item.price))
            item.category = request.form.get('category', item.category)

            if 'image' in request.files:
                image = request.files['image']
                if image.filename != '' and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(image_path)
                    item.image = f'images/{filename}'

            db.session.commit()
            return jsonify(item.to_dict())
        return jsonify({'error': 'Item not found'}), 404
    else:
        if 'name' not in request.form or 'price' not in request.form or 'category' not in request.form:
            return jsonify({'error': 'Missing required fields'}), 400

        new_item = MenuItem(
            name=request.form['name'],
            price=float(request.form['price']),
            category=request.form['category']
        )

        if 'image' in request.files:
            image = request.files['image']
            if image.filename != '' and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                new_item.image = f'images/{filename}'

        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict()), 201

@app.route('/api/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'status': 'success'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        employee = Employee.query.filter_by(login=login).first()

        if employee and employee.verify_password(password):
            session['employee_id'] = employee.id
            session['employee_name'] = employee.name
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Неверный логин или пароль')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'employee_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', employee_name=session['employee_name'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/complete-order/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    if 'employee_id' not in session:
        return jsonify({'error': 'Not authorized'}), 401

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404

    order.status = 'Завершен'
    order.completed_at = datetime.now()
    db.session.commit()

    return jsonify({'status': 'success'})

def calculate_total_price():
    return 0

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

















