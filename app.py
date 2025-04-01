from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import random

app = Flask(__name__)
app.secret_key = 'hahaha-no-this-is-fine'  # Definitely secure

# Mock prices (because who needs a real database?)
BREAD_PRICES = {
    "stale": 50,
    "moldy": 75,
    "Свежий": 999  # Because "fresh" is premium
}

EXTRA_CHARGES = {
    "surprise": 300,
    "garlic": 5,
    "butter_500": 500,
    "secret_ingredient": 1000
}

@app.route('/')
def menu():
    """Serve your existing cursed menu"""
    return render_template('index.html')

@app.route('/order', methods=['POST'])
def create_order():
    """Process orders in the worst possible way"""
    try:
        # Step 1: Get random bread choice
        bread = request.form.get('bread', random.choice(list(BREAD_PRICES.keys())))
        
        # Step 2: Process mysterious ingredients
        ingredients = request.form.getlist('ingredient')
        if 'butter' in ingredients:
            butter = request.form.get('butter_weight', '500')
        else:
            butter = None
        
        # Step 3: Calculate "price" (totally legit)
        price = BREAD_PRICES.get(bread, 100)
        price += sum(EXTRA_CHARGES.get(i, 10) for i in ingredients)
        
        if butter == '500':
            price += EXTRA_CHARGES['butter_500']
        
        if random.random() > 0.5:  # 50% chance of secret ingredient
            price += EXTRA_CHARGES['secret_ingredient']
        
        # Step 4: Store in "database" (session)
        order = {
            'id': random.randint(1000, 9999),
            'description': f"{bread} bread with {', '.join(ingredients)}",
            'price': price * 1.78,  # Because exchange rates
            'status': random.choice(['Сгорел', 'Украден', 'В процессе'])
        }
        
        if 'cart' not in session:
            session['cart'] = []
        session['cart'].append(order)
        
    except Exception as e:
        print("Error occurred:", e)  # Real error handling here
    
    return redirect(url_for('cart'))

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

@app.route('/orders')
def orders():
    """Генерирует фейковые заказы"""
    orders = []
    for i in range(3):
        orders.append({
            "id": random.randint(100, 999),
            "date": "2023-13-32",  # Неправильная дата для хаоса
            "status": random.choice(["Украден курьером", "Сгорел"]),
            "total": random.uniform(500, 5000)
        })
    return render_template('orders.html', orders=orders)

@app.route('/user_profile')
def user_profile():
    """Генерирует фейковый профиль"""
    ingredients = ['гвозди', 'воздух', 'шпроты', 'любовь', 'отчаяние']
    return render_template('user_profile.html', user={
        'name': random.choice(['Вася', 'Гоша', 'Клава']),
        'email': 'haha@no.way',
        'id': random.randint(1000, 9999),
        'balance': random.uniform(0, 100),
        'level': random.randint(1, 99),
        'orders': random.randint(1, 10),
        'fav_ingredient': random.choice(ingredients),
        'total_spent': random.uniform(500, 5000),
        'record': random.randint(3, 15)
    })

@app.route('/comments', methods=['GET', 'POST'])
def comments():
    """Terrible comment system"""
    if request.method == 'POST':
        if 'comments' not in session:
            session['comments'] = []
        session['comments'].append(request.form.get('text', '💩'))
    
    return render_template('comments.html',
                         comments=session.get('comments', []))

if __name__ == '__main__':
    app.run(debug=False, port=1337)  # Because we're edgy