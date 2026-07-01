from flask import Flask, render_template_string, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
import json

app = Flask(__name__)
app.secret_key = "error_x_secret_2026"

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, "error_x.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

BOT_TOKEN = "8290702872:AAF0Kymg0pjJNZNzpyzmS2qTwmiPNNDvGR0"
ACCESS_KEY = "ERROR-X-OWNER"
ADMIN_KEY = "ERROR-X-ADMIN"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(100))
    ip = db.Column(db.String(50))
    device = db.Column(db.String(200))
    access_token = db.Column(db.String(200))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_banned = db.Column(db.Boolean, default=False)

class BannedIP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(50), unique=True)
    banned_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def get_next_display_id():
    last = User.query.order_by(User.display_id.desc()).first()
    return last.display_id + 1 if last else 1001

def is_ip_banned(ip):
    return BannedIP.query.filter_by(ip=ip).first() is not None

def send_to_telegram(text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={'chat_id': '@Errorzlive', 'text': text, 'parse_mode': 'HTML'}, timeout=5)
    except:
        pass

def call_api(url, params):
    try:
        rsp = requests.get(url, params=params, timeout=15)
        try:
            data = json.loads(rsp.text)
            if data.get("data", {}).get("error"):
                return False, f"API Error: {data['data']['error']}"
            if data.get("error"):
                return False, f"API Error: {data['error']}"
            return True, data
        except:
            return rsp.status_code == 200, rsp.text[:200]
    except Exception as e:
        return False, str(e)

CSS = """<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Courier New',monospace}
body{min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px;position:relative;overflow:hidden}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;background:url('https://i.ibb.co/C3rBq6cV/photo-AQADQBBr-Gx-m-GFZ9.jpg');background-size:cover;background-position:center;background-repeat:no-repeat;opacity:0.15;z-index:-1;pointer-events:none}
.card{background:rgba(10,10,10,0.92);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-radius:30px;padding:40px;max-width:500px;width:100%;border:1px solid #ff000066;box-shadow:0 0 60px rgba(255,0,0,0.1);position:relative;z-index:1}
.card h1{font-size:22px;color:#ff0000;text-align:center;margin-bottom:25px}
.input-group{margin-bottom:18px}.input-group label{display:block;color:#ff000088;font-size:11px;margin-bottom:6px;text-transform:uppercase;letter-spacing:1px}
.input-group input,.input-group select{width:100%;padding:12px 16px;background:rgba(255,0,0,0.04);border:1px solid #ff000033;border-radius:12px;color:#ff6666;font-size:14px;transition:.3s}
.input-group input:focus{outline:none;border-color:#ff0000;box-shadow:0 0 20px rgba(255,0,0,0.1)}
.btn{width:100%;padding:12px;background:linear-gradient(135deg,#ff0000,#cc0000);border:none;border-radius:12px;color:#0a0a0a;font-weight:bold;cursor:pointer;font-size:15px;transition:.3s;letter-spacing:1px}
.btn:hover{transform:translateY(-2px);box-shadow:0 10px 40px rgba(255,0,0,0.3)}
.error{background:rgba(255,0,0,0.15);border:1px solid #ff000066;border-radius:12px;padding:12px;margin-bottom:20px;text-align:center;color:#ff6666;font-size:12px}
.success{background:rgba(0,255,0,0.1);border:1px solid #00ff0066;border-radius:12px;padding:12px;margin-bottom:20px;text-align:center;color:#66ff66;font-size:12px}
.back-link{display:block;text-align:center;margin-top:20px;color:#ff000088;text-decoration:none;font-size:12px;letter-spacing:1px}
.back-link:hover{color:#ff0000}
</style>"""

INDEX_HTML = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>ERROR X</title>{CSS}<style>
.logo{{text-align:center;margin-bottom:25px}}
.logo h1{{font-size:32px;font-weight:900;background:linear-gradient(135deg,#ff0000,#cc0000);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.logo p{{color:#ff000088;font-size:13px;margin-top:5px}}
.sub{{color:#ff000088;text-align:center;font-size:12px;margin-bottom:25px;letter-spacing:2px}}
.footer{{text-align:center;margin-top:25px;font-size:10px;color:#ff000044}}
.admin-btn{{display:block;width:100%;padding:12px;margin-top:10px;background:rgba(255,0,0,0.08);border:1px solid #ff000044;border-radius:12px;color:#ff000088;text-align:center;text-decoration:none;font-size:13px;transition:.3s}}
.admin-btn:hover{{background:rgba(255,0,0,0.18);border-color:#ff0000;color:#ff6666}}
</style></head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<div class="logo"><h1>ERROR X</h1><p>BIND TOOL</p></div>
<p class="sub">ENTER ACCESS KEY</p>
{{% if error %}}<div class="error">{{{{ error }}}}</div>{{% endif %}}
<form method="POST" action="/login"><div class="input-group"><label>ACCESS KEY</label><input type="password" name="key" placeholder="ENTER ACCESS KEY" required autofocus></div>
<button type="submit" class="btn">ACCESS</button></form>
<div class="footer"><a href="https://t.me/Errorzlive" style="color:#ff000088;">SUPPORT</a>
<a href="/admin-login" class="admin-btn">ADMIN PANEL</a><br><br>DEVELOPER - @Errorzlive</div></div></div></body></html>"""

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return render_template_string(INDEX_HTML)

@app.route('/login', methods=['POST'])
def login():
    key = request.form.get('key')
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', '')
    if is_ip_banned(ip):
        return render_template_string(INDEX_HTML, error="YOU ARE BANNED!")
    if key != ACCESS_KEY:
        return render_template_string(INDEX_HTML, error="INVALID ACCESS KEY!")
    existing = User.query.filter_by(ip=ip).first()
    if existing:
        if existing.is_banned:
            return render_template_string(INDEX_HTML, error="YOU ARE BANNED!")
        session['user_id'] = existing.id
        return redirect('/dashboard')
    user = User(display_id=get_next_display_id(), ip=ip, device=ua[:200])
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    send_to_telegram(f"🔔 NEW LOGIN\nID: {user.display_id}\nIP: {ip}")
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    user = User.query.get(session['user_id'])
    if not user or user.is_banned:
        session.clear()
        return redirect('/')
    at = request.args.get('access_token', user.access_token)
    if at and at != user.access_token:
        user.access_token = at; db.session.commit()
    bind = None
    if user.access_token:
        ok, data = call_api("https://bindinfocrownx612.vercel.app/check", {'access_token': user.access_token})
        if ok:
            inner = data.get("data", data)
            bind = {'status': inner.get('status','N/A'), 'current_email': inner.get('current_email','N/A'),
                    'pending_email': inner.get('pending_email','N/A'), 'email_to_be': inner.get('email_to_be','N/A'),
                    'countdown': inner.get('countdown_human','N/A')}
    return render_template_string("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Dashboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Courier New',monospace}
body{background:#0a0a0a;min-height:100vh;color:#ff6666}
.navbar{background:rgba(10,10,10,0.95);padding:15px 25px;display:flex;justify-content:space-between;border-bottom:1px solid #ff000033}
.navbar h1{font-size:20px;color:#ff0000}
.nav-right{display:flex;align-items:center;gap:15px}
.nav-right .id-badge{color:#ff000088;font-size:11px;border:1px solid #ff000033;padding:4px 14px;border-radius:20px}
.container{padding:30px;max-width:900px;margin:0 auto}
.info-card{background:rgba(255,0,0,0.03);border-radius:20px;padding:25px;border:1px solid #ff000022;margin-bottom:30px}
.btn-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:20px}
.btn-grid a{padding:14px 10px;background:linear-gradient(135deg,#ff0000,#cc0000);border:none;border-radius:12px;color:#0a0a0a;font-weight:bold;cursor:pointer;text-decoration:none;text-align:center;font-size:12px;transition:.3s}
.btn-grid a:hover{transform:translateY(-2px);box-shadow:0 10px 40px rgba(255,0,0,0.3)}
.btn-ghost{padding:12px 25px;background:transparent;border:1px solid #ff000044;border-radius:12px;color:#ff6666;text-decoration:none;display:inline-block;text-align:center;font-size:13px;transition:.3s}
.btn-ghost:hover{background:rgba(255,0,0,0.08)}
.footer{text-align:center;margin-top:40px;font-size:10px;color:#ff000044;padding:15px;border-top:1px solid #ff000011}
.info-row{padding:8px 0;border-bottom:1px solid rgba(255,0,0,0.08);display:flex;justify-content:space-between;font-size:13px}
.info-row .label{color:#ff000088}
.info-row .value{color:#ff6666;font-weight:bold}
@media(max-width:600px){.btn-grid{grid-template-columns:1fr 1fr}}
</style></head>
<body><div class="navbar"><h1>ERROR X</h1><div class="nav-right"><span class="id-badge">ID: """ + str(user.display_id) + """</span></div></div>
<div class="container">
<div class="info-card"><h2 style="color:#ff0000;margin-bottom:15px">RECOVERY MAIL INFO</h2>
{% if bind %}
<div class="info-row"><span class="label">STATUS</span><span class="value">{{ bind.status }}</span></div>
<div class="info-row"><span class="label">CURRENT EMAIL</span><span class="value">{{ bind.current_email }}</span></div>
<div class="info-row"><span class="label">PENDING</span><span class="value">{{ bind.pending_email }}</span></div>
<div class="info-row"><span class="label">TO BE</span><span class="value">{{ bind.email_to_be }}</span></div>
<div class="info-row"><span class="label">TIMER</span><span class="value">{{ bind.countdown }}</span></div>
{% else %}<div class="info-row"><span class="label">Set token below:</span></div>{% endif %}
<form method="GET" action="/dashboard" style="display:flex;gap:10px;margin-top:15px">
<input type="text" name="access_token" placeholder="Access Token" style="flex:1;padding:12px;background:rgba(255,0,0,0.04);border:1px solid #ff000033;border-radius:12px;color:#ff6666" value='""" + (user.access_token or '') + """'>
<button type="submit" style="padding:12px 25px;background:linear-gradient(135deg,#ff0000,#cc0000);border:none;border-radius:12px;color:#0a0a0a;font-weight:bold;cursor:pointer">FETCH</button></form></div>
<div class="btn-grid">
<a href="/check-bind">CHECK MAIL</a>
<a href="/change-sec">CHANGE (SEC)</a>
<a href="/change-otp">CHANGE (OTP)</a>
<a href="/unbind">UNBIND</a>
<a href="/revoke">REVOKE</a>
<a href="/cancel">CANCEL</a></div>
<div style="text-align:center">
<a href="https://t.me/Errorzlive" class="btn-ghost">TELEGRAM</a>
<a href="/logout" class="btn-ghost" style="margin-left:10px">LOGOUT</a></div></div>
<div class="footer">DEVELOPER - @Errorzlive</div></body></html>""", bind=bind)

@app.route('/check-bind', methods=['GET', 'POST'])
def check_bind_page():
    if 'user_id' not in session:
        return redirect('/')
    result = None; error = None
    if request.method == 'POST':
        at = request.form.get('access_token')
        if at:
            ok, data = call_api("https://bindinfocrownx612.vercel.app/check", {'access_token': at})
            if ok:
                inner = data.get("data", data)
                result = {'status': inner.get('status','N/A'), 'current_email': inner.get('current_email','N/A'),
                         'pending_email': inner.get('pending_email','N/A'), 'email_to_be': inner.get('email_to_be','N/A'),
                         'countdown': inner.get('countdown_human','N/A')}
            else:
                error = data
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Check Bind</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>CHECK RECOVERY MAIL</h1>
{{% if error %}}<div class="error">{{{{ error }}}}</div>{{% endif %}}
{{% if result %}}
<div class="success" style="text-align:left;">
<div><strong>STATUS:</strong> {{{{ result.status }}}}</div>
<div><strong>CURRENT:</strong> {{{{ result.current_email }}}}</div>
<div><strong>PENDING:</strong> {{{{ result.pending_email }}}}</div>
<div><strong>TO BE:</strong> {{{{ result.email_to_be }}}}</div>
<div><strong>TIMER:</strong> {{{{ result.countdown }}}}</div></div>{{% endif %}}
<form method="POST"><div class="input-group"><label>ACCESS TOKEN</label><input type="text" name="access_token" required></div>
<button type="submit" class="btn">CHECK</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""", result=result, error=error)

# ==================== CHANGE WITH OTP (3 STEP) ====================
@app.route('/change-otp', methods=['GET', 'POST'])
def change_otp():
    if 'user_id' not in session:
        return redirect('/')
    error = None; success = None
    
    if request.method == 'POST':
        step = int(request.form.get('step', 1))
        
        if step == 1:
            at = request.form.get('access_token')
            ce = request.form.get('current_email')
            if not at or not ce:
                error = "All fields required!"
            else:
                ok, msg = call_api("https://chngeforgotcrownx72.vercel.app/otp", {'access_token': at, 'current_email': ce})
                if ok:
                    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Step 2</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>STEP 2 - VERIFY CURRENT EMAIL</h1>
<p style="color:#00ff0088;text-align:center;margin-bottom:20px">✓ OTP sent to {ce}</p>
<form method="POST">
<div class="input-group"><label>OTP (CURRENT EMAIL)</label><input type="text" name="otp1" required></div>
<div class="input-group"><label>NEW EMAIL</label><input type="email" name="new_email" required></div>
<input type="hidden" name="step" value="2">
<input type="hidden" name="access_token" value=\"""" + at + """\">
<input type="hidden" name="current_email" value=\"""" + ce + """\">
<button type="submit" class="btn">VERIFY & SEND OTP TO NEW</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""")
                else:
                    error = f"OTP send failed: {msg}"
        
        elif step == 2:
            at = request.form.get('access_token'); ce = request.form.get('current_email')
            otp1 = request.form.get('otp1'); ne = request.form.get('new_email')
            if not all([at, ce, otp1, ne]):
                error = "All fields required!"
            else:
                ok1, _ = call_api("https://chngeforgotcrownx72.vercel.app/verify", {'access_token': at, 'current_email': ce, 'otp': otp1})
                if not ok1:
                    error = "Invalid OTP for current email!"
                else:
                    ok2, _ = call_api("https://chngeforgotcrownx72.vercel.app/newotp", {'access_token': at, 'new_email': ne})
                    if not ok2:
                        error = "Failed to send OTP to new email!"
                    else:
                        return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Step 3</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>STEP 3 - VERIFY NEW EMAIL</h1>
<p style="color:#00ff0088;text-align:center;margin-bottom:20px">✓ OTP sent to {ne}</p>
<form method="POST">
<div class="input-group"><label>OTP (NEW EMAIL)</label><input type="text" name="otp2" required></div>
<input type="hidden" name="step" value="3">
<input type="hidden" name="access_token" value=\"""" + at + """\">
<input type="hidden" name="current_email" value=\"""" + ce + """\">
<input type="hidden" name="new_email" value=\"""" + ne + """\">
<input type="hidden" name="otp1" value=\"""" + otp1 + """\">
<button type="submit" class="btn">FINAL CHANGE</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""")
        
        elif step == 3:
            at = request.form.get('access_token'); ce = request.form.get('current_email')
            ne = request.form.get('new_email'); otp2 = request.form.get('otp2'); otp1 = request.form.get('otp1')
            
            ok_id, d_id = call_api("https://chngeforgotcrownx72.vercel.app/verify", {'access_token': at, 'current_email': ce, 'otp': otp1})
            if not ok_id:
                error = "Identity verification failed!"
            else:
                identity = d_id.get('identity_token') or d_id.get('data',{}).get('identity_token','')
                ok_v, d_v = call_api("https://chngeforgotcrownx72.vercel.app/newverify", {'access_token': at, 'new_email': ne, 'otp': otp2})
                if not ok_v:
                    error = "Invalid OTP for new email!"
                else:
                    verifier = d_v.get('verifier_token') or d_v.get('data',{}).get('verifier_token','')
                    ok_c, _ = call_api("https://chngeforgotcrownx72.vercel.app/change", {'access_token': at, 'new_email': ne, 'identity_token': identity, 'verifier_token': verifier})
                    if ok_c:
                        success = f"✅ Email changed to {ne}!"
                        send_to_telegram(f"✅ EMAIL CHANGED (OTP)\nNew: {ne}")
                    else:
                        error = "Change failed!"
    
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Change OTP</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>CHANGE MAIL (OTP)</h1>
{{% if error %}}<div class="error">{{{{ error }}}}</div>{{% endif %}}
{{% if success %}}<div class="success">{{{{ success }}}}</div>{{% endif %}}
<form method="POST"><div class="input-group"><label>ACCESS TOKEN</label><input type="text" name="access_token" required></div>
<div class="input-group"><label>CURRENT EMAIL</label><input type="email" name="current_email" required></div>
<input type="hidden" name="step" value="1">
<button type="submit" class="btn">SEND OTP TO CURRENT</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""", error=error, success=success)

# ==================== CHANGE WITH SEC ====================
@app.route('/change-sec', methods=['GET', 'POST'])
def change_sec():
    if 'user_id' not in session:
        return redirect('/')
    error = None; success = None; show_otp = False; hd = {}
    
    if request.method == 'POST':
        step = request.form.get('step', '1')
        if step == '1':
            at = request.form.get('access_token'); ce = request.form.get('current_email')
            sc = request.form.get('sec_code'); ne = request.form.get('new_email')
            if not all([at, ce, sc, ne]):
                error = "All fields required!"
            else:
                ok, _ = call_api("https://chngemailcode48.vercel.app/send_otp", {'access_token': at, 'email': ne})
                if ok:
                    show_otp = True; hd = {'access_token': at, 'current_email': ce, 'sec_code': sc, 'new_email': ne}
                else:
                    error = "OTP send failed!"
        
        elif step == '2':
            at = request.form.get('access_token'); ce = request.form.get('current_email')
            sc = request.form.get('sec_code'); ne = request.form.get('new_email')
            otp = request.form.get('otp_new')
            ok_id, d_id = call_api("https://chngemailcode48.vercel.app/verify_identity", {'access_token': at, 'code': sc})
            if not ok_id:
                error = "Invalid security code!"; show_otp = True; hd = request.form
            else:
                identity = d_id.get('identity_token') or d_id.get('data',{}).get('identity_token','')
                ok_v, d_v = call_api("https://chngemailcode48.vercel.app/verify_otp", {'access_token': at, 'email': ne, 'otp': otp})
                if not ok_v:
                    error = "Invalid OTP!"; show_otp = True; hd = request.form
                else:
                    verifier = d_v.get('verifier_token') or d_v.get('data',{}).get('verifier_token','')
                    ok_c, _ = call_api("https://chngemailcode48.vercel.app/create_rebind", {'access_token': at, 'email': ne, 'identity_token': identity, 'verifier_token': verifier})
                    if ok_c:
                        success = f"✅ Email changed to {ne}!"
                        send_to_telegram(f"✅ EMAIL CHANGED (SEC)\nNew: {ne}")
                    else:
                        error = "Change failed!"; show_otp = True; hd = request.form
    
    if show_otp:
        return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Enter OTP</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>ENTER OTP</h1>
<p style="color:#00ff0088;text-align:center;margin-bottom:20px">OTP sent to {hd.get('new_email','')}</p>
{{% if error %}}<div class="error">{{{{ error }}}}</div>{{% endif %}}
{{% if success %}}<div class="success">{{{{ success }}}}</div>{{% endif %}}
<form method="POST"><div class="input-group"><label>OTP CODE</label><input type="text" name="otp_new" required></div>
<input type="hidden" name="step" value="2">
<input type="hidden" name="access_token" value=\"""" + hd.get('access_token','') + """\">
<input type="hidden" name="current_email" value=\"""" + hd.get('current_email','') + """\">
<input type="hidden" name="sec_code" value=\"""" + hd.get('sec_code','') + """\">
<input type="hidden" name="new_email" value=\"""" + hd.get('new_email','') + """\">
<button type="submit" class="btn">CHANGE</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""", error=error, success=success)
    
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Change SEC</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>CHANGE MAIL (SEC)</h1>
{{% if error %}}<div class="error">{{{{ error }}}}</div>{{% endif %}}
{{% if success %}}<div class="success">{{{{ success }}}}</div>{{% endif %}}
<form method="POST"><div class="input-group"><label>ACCESS TOKEN</label><input type="text" name="access_token" required></div>
<div class="input-group"><label>CURRENT EMAIL</label><input type="email" name="current_email" required></div>
<div class="input-group"><label>SECURITY CODE</label><input type="text" name="sec_code" required></div>
<div class="input-group"><label>NEW EMAIL</label><input type="email" name="new_email" required></div>
<input type="hidden" name="step" value="1">
<button type="submit" class="btn">SEND OTP</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""", error=error, success=success)

# ==================== UNBIND ====================
@app.route('/unbind', methods=['GET', 'POST'])
def unbind():
    if 'user_id' not in session:
        return redirect('/')
    if request.method == 'POST':
        at = request.form.get('access_token'); sc = request.form.get('sec_code')
        ce = request.form.get('current_email'); otp = request.form.get('otp')
        if sc:
            ok, _ = call_api("https://crownxnewkey10010.vercel.app/securityunbind", {'access_token': at, 'security_code': sc})
            if ok:
                send_to_telegram("🔓 UNBIND (SEC)")
                return render_template_string(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Done</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card"><h1>DONE</h1><div class="success">15 Days Timer Started!</div><a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""")
        elif ce and otp:
            call_api("https://chngeforgotcrownx72.vercel.app/otp", {'access_token': at, 'current_email': ce})
            ok, d = call_api("https://chngeforgotcrownx72.vercel.app/verify", {'access_token': at, 'current_email': ce, 'otp': otp})
            if ok:
                identity = d.get('identity_token') or d.get('data',{}).get('identity_token','')
                ok2, _ = call_api("https://crownxforgotremove23.vercel.app/forgotunbind", {'access_token': at, 'identity_token': identity})
                if ok2:
                    send_to_telegram("🔓 UNBIND (OTP)")
                    return render_template_string(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Done</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card"><h1>DONE</h1><div class="success">15 Days Timer Started!</div><a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""")
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Unbind</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>UNBIND</h1>
<form method="POST"><div class="input-group"><label>ACCESS TOKEN</label><input type="text" name="access_token" required></div>
<div class="input-group"><label>SECURITY CODE</label><input type="text" name="sec_code"></div>
<div class="input-group"><label>CURRENT EMAIL (OTP)</label><input type="email" name="current_email"></div>
<div class="input-group"><label>OTP</label><input type="text" name="otp"></div>
<button type="submit" class="btn">UNBIND</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""")

# ==================== REVOKE ====================
@app.route('/revoke', methods=['GET', 'POST'])
def revoke():
    if 'user_id' not in session:
        return redirect('/')
    error=None;success=None
    if request.method=='POST':
        at=request.form.get('access_token')
        if at:
            ok,msg=call_api("https://crownxrevoker73.vercel.app/revoke",{'access_token':at})
            if ok: success="Token revoked!"; send_to_telegram("🔑 TOKEN REVOKED")
            else: error=msg
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Revoke</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>REVOKE</h1>
{{% if error %}}<div class="error">{{{{ error }}}}</div>{{% endif %}}
{{% if success %}}<div class="success">{{{{ success }}}}</div>{{% endif %}}
<form method="POST"><div class="input-group"><label>ACCESS TOKEN</label><input type="text" name="access_token" required></div>
<button type="submit" class="btn">REVOKE</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""", error=error, success=success)

# ==================== CANCEL ====================
@app.route('/cancel', methods=['GET', 'POST'])
def cancel():
    if 'user_id' not in session: return redirect('/')
    error=None;success=None
    if request.method=='POST':
        at=request.form.get('access_token')
        if at:
            ok,msg=call_api("https://bindcnclcrownx34.vercel.app/cancelbind",{'access_token':at})
            if ok: success="Cancelled!"; send_to_telegram("❌ BIND CANCELLED")
            else: error=msg
    return render_template_string(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Cancel</title>{CSS}</head>
<body><div style="width:100%;max-width:500px;padding:20px"><div class="card">
<h1>CANCEL</h1>
{{% if error %}}<div class="error">{{{{ error }}}}</div>{{% endif %}}
{{% if success %}}<div class="success">{{{{ success }}}}</div>{{% endif %}}
<form method="POST"><div class="input-group"><label>ACCESS TOKEN</label><input type="text" name="access_token" required></div>
<button type="submit" class="btn">CANCEL</button></form>
<a href="/dashboard" class="back-link">← BACK</a></div></div></body></html>""", error=error, success=success)

# ==================== ADMIN ====================
@app.route('/admin-login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        if request.form.get('key')==ADMIN_KEY: session['admin']=True; return redirect('/admin')
        return render_template_string(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Admin</title>{CSS}</head>
<body><div style="width:100%;max-width:450px;padding:20px"><div class="card"><h1>ADMIN</h1><div class="error">INVALID KEY!</div>
<form method="POST"><div class="input-group"><label>ADMIN KEY</label><input type="password" name="key" required></div>
<button type="submit" class="btn">ACCESS</button></form></div></div></body></html>""")
    return render_template_string(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Admin</title>{CSS}</head>
<body><div style="width:100%;max-width:450px;padding:20px"><div class="card"><h1>ADMIN</h1>
<form method="POST"><div class="input-group"><label>ADMIN KEY</label><input type="password" name="key" required></div>
<button type="submit" class="btn">ACCESS</button></form></div></div></body></html>""")

@app.route('/admin')
def admin():
    if not session.get('admin'): return redirect('/admin-login')
    users=User.query.order_by(User.display_id).all()
    ips=BannedIP.query.all()
    return render_template_string("""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Admin</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Courier New',monospace}
body{background:#0a0a0a;min-height:100vh;color:#ff6666}
.navbar{background:rgba(10,10,10,0.95);padding:15px 25px;display:flex;justify-content:space-between;border-bottom:1px solid #ff000033}
.navbar h1{font-size:20px;color:#ff0000}.navbar a{color:#ff000088;text-decoration:none;padding:8px 16px;border:1px solid #ff000033;border-radius:8px}
.container{padding:25px;max-width:1200px;margin:0 auto}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:15px;margin-bottom:25px}
.stat-card{background:rgba(255,0,0,0.03);border:1px solid #ff000022;border-radius:15px;padding:20px;text-align:center}
.stat-card h3{color:#ff000088;font-size:11px}.stat-card .value{color:#ff0000;font-size:28px;font-weight:bold}
.section{background:rgba(255,0,0,0.03);border-radius:15px;padding:20px;margin-bottom:20px;border:1px solid #ff000022}
.section h2{color:#ff0000;font-size:16px;margin-bottom:15px}
table{width:100%;border-collapse:collapse;font-size:12px}
th,td{padding:10px;text-align:left;border-bottom:1px solid #ff000011;color:#ff6666}
th{color:#ff000088}
.ban-btn{background:#ff333355;border:none;padding:4px 12px;border-radius:6px;color:#ff6666;cursor:pointer}
.unban-btn{background:#33ff3355;border:none;padding:4px 12px;border-radius:6px;color:#66ff66;cursor:pointer}
.ip-btn{background:#ff880055;border:none;padding:4px 12px;border-radius:6px;color:#ff8866;cursor:pointer}
</style></head>
<body><div class="navbar"><h1>ADMIN</h1><a href="/logout">LOGOUT</a></div>
<div class="container"><div class="stats">
<div class="stat-card"><h3>TOTAL</h3><div class="value">{{ users|length }}</div></div>
<div class="stat-card"><h3>BANNED</h3><div class="value">{{ users|selectattr('is_banned','eq',True)|list|length }}</div></div>
<div class="stat-card"><h3>BANNED IPs</h3><div class="value">{{ ips|length }}</div></div></div>
<div class="section"><h2>USERS</h2>
<table><tr><th>ID</th><th>IP</th><th>JOINED</th><th>STATUS</th><th>ACTION</th></tr>
{% for u in users %}
<tr><td>{{ u.display_id }}</td><td>{{ u.ip or '-' }}</td><td>{{ u.joined_at.strftime('%Y-%m-%d') if u.joined_at else '-' }}</td>
<td>{{ 'BANNED' if u.is_banned else 'ACTIVE' }}</td>
<td>{% if u.is_banned %}<form action="/admin/unban" method="POST" style="display:inline"><input type="hidden" name="id" value="{{ u.id }}"><button class="unban-btn">UNBAN</button></form>
{% else %}<form action="/admin/ban" method="POST" style="display:inline"><input type="hidden" name="id" value="{{ u.id }}"><button class="ban-btn">BAN</button></form>
<form action="/admin/ban-ip" method="POST" style="display:inline"><input type="hidden" name="ip" value="{{ u.ip }}"><button class="ip-btn">IP BAN</button></form>{% endif %}</td></tr>
{% endfor %}</table></div>
<div class="section"><h2>BANNED IPS</h2>
<table><tr><th>IP</th><th>ACTION</th></tr>
{% for b in ips %}<tr><td>{{ b.ip }}</td>
<td><form action="/admin/unban-ip" method="POST"><input type="hidden" name="ip" value="{{ b.ip }}"><button class="unban-btn">UNBAN</button></form></td></tr>
{% endfor %}</table></div></div></body></html>""", users=users, ips=ips)

@app.route('/admin/ban', methods=['POST'])
def admin_ban_u():
    if session.get('admin'):
        u=db.session.get(User,int(request.form['id']))
        if u: u.is_banned=True; db.session.commit()
    return redirect('/admin')

@app.route('/admin/unban', methods=['POST'])
def admin_unban_u():
    if session.get('admin'):
        u=db.session.get(User,int(request.form['id']))
        if u: u.is_banned=False; db.session.commit()
    return redirect('/admin')

@app.route('/admin/ban-ip', methods=['POST'])
def admin_ban_ip():
    if session.get('admin'):
        ip=request.form.get('ip')
        if ip and not is_ip_banned(ip):
            db.session.add(BannedIP(ip=ip))
            u=User.query.filter_by(ip=ip).first()
            if u: u.is_banned=True
            db.session.commit()
    return redirect('/admin')

@app.route('/admin/unban-ip', methods=['POST'])
def admin_unban_ip():
    if session.get('admin'):
        ip=request.form.get('ip')
        b=BannedIP.query.filter_by(ip=ip).first()
        if b: db.session.delete(b); db.session.commit()
    return redirect('/admin')

@app.route('/logout')
def logout(): session.clear(); return redirect('/')

@app.errorhandler(404)
def nf(e): return redirect('/')

@app.errorhandler(500)
def se(e): return "Server error", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)