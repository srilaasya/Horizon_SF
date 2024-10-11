from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Simulated database
orders = []

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get data from the form
        customer = request.form.get('customer')
        order = request.form.get('order')
        dietary_restrictions = request.form.get('dietary_restrictions')

        # Add the order to the simulated database
        orders.append({
            'customer': customer,
            'order': order,
            'dietary_restrictions': dietary_restrictions
        })

        # Redirect to the home page to display the updated orders
        return redirect(url_for('home'))

    return render_template('index.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)