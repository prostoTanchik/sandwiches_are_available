from flask import Flask, render_template, request, session, redirect, url_for
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
    return render_template('menu.html')

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

@app.route('/orders')
def orders():
    """Generate fake order history"""
    orders = []
    for i in range(3):
        orders.append({
            'id': random.randint(100, 999),
            'date': '2023-13-32',  # Valid date format
            'status': random.choice(['Съеден', 'Потерян', 'Стал sentient']),
            'total': random.uniform(100, 1000)
        })
    return render_template('orders.html', orders=orders)

@app.route('/user_profile')
def user_profile():
    """Generate random user profile"""
    return render_template('user_profile.html',
                         user={
                             'name': random.choice(['Вася', 'Гоша', 'Клава']),
                             'email': 'haha@no.way',
                             'bio': 'Professional sandwich sufferer'
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