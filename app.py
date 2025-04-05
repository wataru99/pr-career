from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_user_func"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return redirect(url_for('login_user_func'))

@app.route('/login', methods=['GET', 'POST'])
def login_user_func():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template('login.html', error="ユーザー名が異なります。")
        if not check_password_hash(user.password, password):
            return render_template('login.html', error="パスワードが間違っています。")
        login_user(user)
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_user_func'))

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="そのユーザー名はすでに使用されています。")
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('register_complete'))
    return render_template('register.html')

@app.route('/register-complete')
def register_complete():
    return render_template('register_complete.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', username=current_user.username)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/password-reset', methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        return render_template('password_reset_complete.html')
    return render_template('password_reset.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404 

@app.route('/ai-diagnosis-questions', methods=['GET', 'POST'])
@login_required
def ai_diagnosis_questions_page():
    return render_template('ai_diagnosis_questions.html')

@app.route('/ai_diagnosis_result', methods=['GET', 'POST'])
@login_required
def ai_diagnosis_result():
    if request.method == 'POST':
        # フォームからの入力データの受け取り（必要に応じて利用可能）
        experience = request.form.get('experience')
        skills = request.form.get('skills')
        future = request.form.get('future')
        return render_template('ai_diagnosis_result.html', experience=experience, skills=skills, future=future)
    return render_template('ai_diagnosis_result.html')


# --- その他のHTMLテンプレートへのルートを追加 ---
extra_pages = [
    'achievements', 'ai_diagnosis', 'application_status',
    'blocked_users', 'company', 'company_detail', 'contact', 'contact_complete', 'contact_detail', 'contact_list',
    'contact_reply', 'faq', 'favorites', 'former_pr', 'job_applicants', 'job_application_detail', 'job_listings',
    'job_posting', 'job_search_results', 'job_seekers', 'media_coverage', 'message_history',
    'narrator', 'notification_settings', 'password_reset_complete', 'pricing', 'privacy', 'profile_edit',
    'profile_visibility', 'scout', 'scout_complete', 'scout_form', 'sitemap', 'stage_actor', 'system_settings',
    'takara', 'terms', 'user_notifications', 'withdraw_complete', 'withdrawal_confirm',
    'admin_dashboard', 'announcer', 'athlete', 'comedian'
    # 'ai_diagnosis_result' はすでに個別定義しているため除外
]


for page in extra_pages:
    route_path = f"/{page.replace('_', '-')}"
    template_file = f"{page}.html"
    app.add_url_rule(route_path, page, lambda p=template_file: render_template(p))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
