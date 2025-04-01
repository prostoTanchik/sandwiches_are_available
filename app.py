from flask import Flask, render_template, request, session, redirect, url_for, jsonify, make_response
import random
from datetime import datetime, timedelta
import psycopg2
from psycopg2 import sql
import random

app = Flask(__name__)
app.secret_key = 'poopoo-peepee'

EXTRA_CHARGES = {
    "surprise": 300,
    "garlic": 5,
    "butter_500": 500,
    "secret_ingredient": 1000
}

# Подключение к PostgreSQL (настройте под свою БД)
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="buters_db",
        user="postgres",
        password="postgres"  # Очень безопасно!
    )
    return conn

# Создаем таблицы при первом запуске (если их нет)
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Таблица пользователей (с максимально неудобными полями)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username VARCHAR(50) UNIQUE NOT NULL, 
            password TEXT,
            email VARCHAR(100),
            mother_maiden_name TEXT,
            birth_city TEXT,
            first_pet TEXT,
            first_teacher TEXT,
            childhood_school TEXT,
            first_car TEXT,
            favorite_media TEXT,
            grandparent_profession TEXT,
            parents_wedding_date TEXT,
            childhood_street TEXT,
            is_pigeon BOOLEAN DEFAULT FALSE
        )
        """)
        
        # Таблица заказов (полный хаос)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            description TEXT,
            price DECIMAL(10, 2),
            status VARCHAR(50) DEFAULT 'lost',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

# Инициализируем БД при старте
init_db()

@app.route('/')
def menu():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    global REGISTRATION_CLOSED
    
    # Проверяем куки (хотя они все равно ни на что не влияют)
    registration_closed_cookie = request.cookies.get('registration_closed') == 'true'
    
    
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Получаем данные формы (но валидация - для слабаков)
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Проверяем, существует ли пользователь (но нам все равно)
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                return render_template('registration.html', 
                                    error="Имя пользователя уже существует (но вы все равно попробуйте еще раз)")
            
            # Генерируем "защиту" пароля (это же просто цифра!)
            salt = str(random.randint(0, 9))  # Супер-безопасно!
            
            # Сохраняем ВСЕ данные (потому что мы коллекционеры)
            cur.execute("""
            INSERT INTO users (
                username, 
                password,  -- открытым текстом, конечно
                email,
                mother_maiden_name,
                birth_city,
                first_pet,
                first_teacher,
                childhood_school,
                first_car,
                favorite_media,
                grandparent_profession,
                parents_wedding_date,
                childhood_street,
                is_pigeon
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """, (
                username,
                password + salt,  # "Хэширование" на высшем уровне
                request.form.get('email'),
                request.form.get('motherMaidenName'),
                request.form.get('birthCity'),
                request.form.get('firstPet'),
                request.form.get('firstTeacher'),
                request.form.get('childhoodSchool'),
                request.form.get('firstCar'),
                request.form.get('favoriteMedia'),
                request.form.get('grandparentProfession'),
                request.form.get('parentsWeddingDate'),
                request.form.get('childhoodStreet'),
                random.choice([True, False])
            ))
            
            conn.commit()
            
            # Устанавливаем сессию (но без user_id, как вы хотели)
            session['username'] = username
            session['is_pigeon'] = random.choice([True, False])  # Важная информация!
            
            # Перенаправляем... куда-то (нам все равно)
            return redirect(url_for('user_profile'))
            
        except Exception as e:
            conn.rollback()
            # Выбираем случайное сообщение об ошибке (правда не важна)
            error_messages = [
                "Ошибка сервера: слишком много голубей",
                "Ваши данные вызвали переполнение",
                "Попробуйте использовать меньше секретов",
                "Сервер не оценил вашу девичью фамилию"
            ]
            return render_template('registration.html', 
                                error=random.choice(error_messages))
        finally:
            if conn:
                conn.close()
    
    return render_template('registration.html')

@app.route('/cart')
def cart():
    """Show cart with questionable contents"""
    cart = session.get('cart', [])
    total = sum(item.get('price', 0) for item in cart)
    return render_template('cart.html', cart=cart, total=total)

# Mock database of cursed sandwiches
MYSTERY_ITEMS = [
    {"description": "Бутерброд с гвоздями", "price": 666.66},
    {"description": "Сэндвич 'Сюрприз из прошлого'", "price": 999.99},
    {"description": "Хлеб с воздухом (премиум)", "price": 500.00},
]

@app.route('/add_mystery_item', methods=['POST'])
def add_mystery_item():
    """Add a random cursed item to cart"""
    if 'cart' not in session:
        session['cart'] = []
    
    mystery_item = random.choice(MYSTERY_ITEMS)
    session['cart'].append(mystery_item)
    session.modified = True
    
    return jsonify({"success": True})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """50% chance to remove wrong item"""
    try:
        index = request.json.get('index')
        if 'cart' in session and 0 <= index < len(session['cart']):
            if random.random() > 0.5:  # 50% chance to remove random item
                index = random.randint(0, len(session['cart'])-1)
            session['cart'].pop(index)
            session.modified = True
    except:
        pass  # Silence is golden
    return jsonify({"success": True})

@app.route('/user_profile')
def user_profile():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Берем случайного пользователя (или создаем нового)
        cur.execute("""
        SELECT username, email, 
               COALESCE(mother_maiden_name, 'неизвестно') AS mother_maiden_name,
               COALESCE(first_pet, 'неизвестно') AS first_pet
        FROM users
        ORDER BY RANDOM() 
        LIMIT 1
        """)
        
        user = cur.fetchone()
        
        if not user:
            # Если пользователей нет - создаем фейкового
            user = (
                1, 
                'Гость', 
                'haha@no.way', 
                'неизвестно', 
                'неизвестно'
            )

        orders = [
            (1, "Фейковый заказ", 999.99, "lost"),
            (2, "Еще один фейковый заказ", 500.00, "eaten")
        ]
        
        return render_template('user_profile.html', 
                             user={
                                 'id': user[0],
                                 'name': user[1],
                                 'email': user[2],
                                 'mother_maiden_name': user[3],
                                 'first_pet_name': user[4],
                                 'balance': random.uniform(0, 100),
                                 'level': random.randint(1, 99),
                                 'orders': len(orders),
                                 'total_spent': sum(order[2] for order in orders),
                                 'record': random.randint(1, 10)
                             })
        
    except Exception as e:
        print(f"Profile error: {e}")
        return render_template('user_profile.html', 
                             user={
                                 'name': 'Ошибка',
                                 'email': 'error@error.com',
                                 'balance': 0,
                                 'level': 0
                             })
    finally:
        if conn:
            conn.close()

@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        cart = request.json.get('cart', [])
        
        # Подключаемся к базе данных
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Добавляем каждый элемент корзины как отдельный заказ
        for item in cart:
            cur.execute(
                "INSERT INTO orders (description, price, status) VALUES (%s, %s, 'lost')",
                (item['description'], item['price'])
            )
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Заказ создан'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return jsonify({'success': True})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Получаем данные из формы
    bread = request.form.get('bread')
    ingredients = request.form.getlist('ingredient')
    butter_weight = request.form.get('butter_weight')
    garlic = request.form.get('garlic') == 'true'
    
    # Создаем описание бутерброда
    description = f"Бутерброд на {bread} хлебе"

    if butter_weight:
        description += f" с {butter_weight}г масла"
    if garlic:
        description += ", с чесночком"
    
    # Добавляем в корзину
    if 'cart' not in session:
        session['cart'] = []
    
    # Простая логика ценообразования
    price = 100
    if bread == 'moldy':
        price += 50
    if 'surprise' in ingredients:
        price += 100
    if garlic:
        price += 5
    
    session['cart'].append({
        'description': description,
        'price': price
    })
    session.modified = True
    
    # Редирект на корзину
    return redirect('/cart')

@app.route('/orders')
def show_orders():
    """Отображает страницу со списком всех заказов"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Получаем все заказы из базы данных
        cur.execute("""
        SELECT 
            id,
            description,
            price,
            status,
            created_at as date
        FROM orders
        ORDER BY created_at DESC
        """)
        
        orders = []
        for order in cur.fetchall():
            orders.append({
                'id': order[0],
                'description': order[1],
                'total': round(float(order[2])),  # Исправлено: добавлена закрывающая скобка
                'status': order[3].upper(),
                'date': order[4].strftime('%Y-%m-%d %H:%M')
            })
        
        return render_template('orders.html', orders=orders)
        
    except Exception as e:
        print(f"Error fetching orders: {e}")
        # В случае ошибки показываем фейковые данные
        fake_orders = [
            {
                'id': 999,
                'description': 'БУТЕРБРОД С ГВОЗДЯМИ',
                'total': 666,
                'status': 'УКРАДЕН',
                'date': '1970-01-01 00:00'
            },
            {
                'id': 404,
                'description': 'ХЛЕБ С ВОЗДУХОМ',
                'total': 999,
                'status': 'СЪЕДЕН',
                'date': '2023-01-01 12:34'
            }
        ]
        return render_template('orders.html', orders=fake_orders)
        
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=False, port=1337)  # Because we're edgy

