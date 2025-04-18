from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy 
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    industry = db.Column(db.String(100), nullable=False)
    goods_type = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Customer {self.name}>'

@app.route('/')
def index():
    customers = Customer.query.with_entities(
        Customer.id, Customer.name, Customer.city, 
        Customer.industry, Customer.goods_type
    ).all()
    return render_template('index.html', customers=customers)

@app.route('/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        city = request.form['city']
        industry = request.form['industry']
        goods_type = request.form['goods_type']
        
        new_customer = Customer(name=name, city=city, industry=industry, goods_type=goods_type)
        
        try:
            db.session.add(new_customer)
            db.session.commit()
            flash('客户添加成功！', 'success')
            return redirect(url_for('index'))
        except:
            flash('添加客户时出错，请重试。', 'danger')
    
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.city = request.form['city']
        customer.industry = request.form['industry']
        customer.goods_type = request.form['goods_type']
        
        try:
            db.session.commit()
            flash('客户信息更新成功！', 'success')
            return redirect(url_for('index'))
        except:
            flash('更新客户信息时出错，请重试。', 'danger')
    
    return render_template('edit.html', customer=customer)

@app.route('/delete/<int:id>')
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('客户删除成功！', 'success')
    except:
        flash('删除客户时出错，请重试。', 'danger')
    
    return redirect(url_for('index'))

@app.route('/api/customer/<name>', methods=['GET'])
def get_customer_by_name(name):
    customer = Customer.query.filter_by(name=name).first()
    if customer:
        return jsonify({
            'id': customer.id,
            'name': customer.name,
            'city': customer.city,
            'industry': customer.industry,
            'goods_type': customer.goods_type
         })
         
    return jsonify({'error': 'Customer not found'}), 404

    
        
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 

