from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists('static/uploads'):
    os.makedirs('static/uploads')

if not os.path.exists('exports'):
    os.makedirs('exports')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ================= USER MODEL =================

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    email = db.Column(db.String(100))

    password = db.Column(db.String(200))

    is_admin = db.Column(db.Boolean, default=False)

    income = db.Column(db.Float, default=0)

    budget = db.Column(db.Float, default=0)


# ================= EXPENSE MODEL =================

class Expense(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    amount = db.Column(db.Float)

    category = db.Column(db.String(100))

    date = db.Column(db.String(100))

    receipt = db.Column(db.String(200))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))


# ================= HOME =================

@app.route('/')
def home():

    return redirect(url_for('login'))


# ================= REGISTER =================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        email = request.form['email']

        password = generate_password_hash(request.form['password'])

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:

            flash('Username already exists')

            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password=password,
            is_admin=True if username == "saqib" else False
        )

        db.session.add(user)

        db.session.commit()

        flash('Registration Successful')

        return redirect(url_for('login'))

    return render_template('register.html')


# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            return redirect(url_for('dashboard'))

        flash('Invalid Username or Password')

    return render_template('login.html')


# ================= DASHBOARD =================

@app.route('/dashboard')
@login_required
def dashboard():

    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    total = sum(exp.amount for exp in expenses)

    categories = {}

    for exp in expenses:

        categories[exp.category] = categories.get(exp.category, 0) + exp.amount

    income = current_user.income

    budget_limit = current_user.budget

    savings = income - total

    remaining_budget = budget_limit - total

    warning = False

    if budget_limit > 0:

        warning = total > budget_limit

    prediction = round((total / 30) * 30, 2)

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total,
        categories=categories,
        savings=savings,
        warning=warning,
        prediction=prediction,
        income=income,
        budget_limit=budget_limit,
        remaining_budget=remaining_budget
    )


# ================= UPDATE FINANCE =================

@app.route('/update_finance', methods=['POST'])
@login_required
def update_finance():

    income = float(request.form['income'])

    budget = float(request.form['budget'])

    current_user.income = income

    current_user.budget = budget

    db.session.commit()

    flash('Finance Details Updated')

    return redirect(url_for('dashboard'))


# ================= ADD EXPENSE =================

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():

    if request.method == 'POST':

        title = request.form['title']

        amount = float(request.form['amount'])

        category = request.form['category']

        receipt = request.files['receipt']

        filename = ''

        if receipt and receipt.filename != '':

            filename = secure_filename(receipt.filename)

            receipt.save(
                os.path.join(app.config['UPLOAD_FOLDER'], filename)
            )

        expense = Expense(
            title=title,
            amount=amount,
            category=category,
            date=datetime.now().strftime('%Y-%m-%d'),
            receipt=filename,
            user_id=current_user.id
        )

        db.session.add(expense)

        db.session.commit()

        flash('Expense Added Successfully')

        return redirect(url_for('dashboard'))

    return render_template('add_expense.html')


# ================= EDIT EXPENSE =================

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_expense(id):

    expense = Expense.query.get_or_404(id)

    if request.method == 'POST':

        expense.title = request.form['title']

        expense.amount = float(request.form['amount'])

        expense.category = request.form['category']

        db.session.commit()

        flash('Expense Updated')

        return redirect(url_for('dashboard'))

    return render_template('edit_expense.html', expense=expense)


# ================= DELETE EXPENSE =================

@app.route('/delete/<int:id>')
@login_required
def delete_expense(id):

    expense = Expense.query.get_or_404(id)

    db.session.delete(expense)

    db.session.commit()

    flash('Expense Deleted')

    return redirect(url_for('dashboard'))


# ================= SEARCH =================

@app.route('/search')
@login_required
def search():

    query = request.args.get('query')

    expenses = Expense.query.filter(
        Expense.title.contains(query)
    ).all()

    total = sum(exp.amount for exp in expenses)

    categories = {}

    for exp in expenses:

        categories[exp.category] = categories.get(exp.category, 0) + exp.amount

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total,
        categories=categories,
        savings=0,
        warning=False,
        prediction=0,
        income=current_user.income,
        budget_limit=current_user.budget,
        remaining_budget=0
    )


# ================= REPORTS =================

@app.route('/reports')
@login_required
def reports():

    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    monthly_data = {}

    for exp in expenses:

        month = exp.date[:7]

        monthly_data[month] = monthly_data.get(month, 0) + exp.amount

    return render_template(
        'reports.html',
        monthly_data=monthly_data
    )


# ================= EXPORT CSV =================

@app.route('/export_csv')
@login_required
def export_csv():

    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    data = []

    for exp in expenses:

        data.append({
            'Title': exp.title,
            'Amount': exp.amount,
            'Category': exp.category,
            'Date': exp.date
        })

    df = pd.DataFrame(data)

    file_path = 'exports/expenses.csv'

    df.to_csv(file_path, index=False)

    return send_file(file_path, as_attachment=True)


# ================= EXPORT PDF =================

@app.route('/export_pdf')
@login_required
def export_pdf():

    file_path = 'exports/report.pdf'

    c = canvas.Canvas(file_path)

    c.drawString(230, 800, 'Expense Report')

    y = 760

    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    for exp in expenses:

        c.drawString(
            100,
            y,
            f'{exp.title} | ₹{exp.amount} | {exp.category}'
        )

        y -= 20

    c.save()

    return send_file(file_path, as_attachment=True)


# ================= PROFILE =================

@app.route('/profile')
@login_required
def profile():

    return render_template('profile.html')


# ================= ADMIN =================

@app.route('/admin')
@login_required
def admin():

    if not current_user.is_admin:

        flash('Access Denied')

        return redirect(url_for('dashboard'))

    users = User.query.all()

    expenses = Expense.query.all()

    return render_template(
        'admin.html',
        users=users,
        expenses=expenses
    )


# ================= LOGOUT =================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(url_for('login'))


# ================= MAIN =================

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(debug=True)