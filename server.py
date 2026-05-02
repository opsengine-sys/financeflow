#!/usr/bin/env python3
"""FinanceFlow Backend Server — Flask + SQLite + JWT + Clerk"""

from flask import Flask, request, jsonify, send_file, g
from flask_cors import CORS
import sqlite3, jwt, bcrypt, uuid, json, os, requests
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app, supports_credentials=True)

SECRET        = os.environ.get('JWT_SECRET', 'ff_jwt_secret_2026_change_in_prod')
CLERK_PUB_KEY = os.environ.get('CLERK_PUBLISHABLE_KEY', '')
CLERK_SECRET  = os.environ.get('CLERK_SECRET_KEY', '')
DB_PATH       = 'financeflow.db'
MKT_HEADERS   = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ─── Clerk Token Verification ─────────────────────────────────────────────────

_clerk_jwks_cache = {'keys': None, 'fetched': 0}

def _get_clerk_jwks():
    """Fetch Clerk JWKS (cached for 5 min)."""
    import time
    now = time.time()
    if _clerk_jwks_cache['keys'] and now - _clerk_jwks_cache['fetched'] < 300:
        return _clerk_jwks_cache['keys']
    if not CLERK_SECRET:
        return None
    # Derive the JWKS URL from the publishable key (pk_live_xxx or pk_test_xxx)
    # Clerk instance domain is embedded in the publishable key
    try:
        # Clerk JWKS endpoint uses the secret key to get the instance
        # We'll call the Clerk backend API to get the JWKS URL
        r = requests.get(
            'https://api.clerk.com/v1/jwks',
            headers={'Authorization': f'Bearer {CLERK_SECRET}'},
            timeout=5
        )
        if r.ok:
            _clerk_jwks_cache['keys'] = r.json().get('keys', [])
            _clerk_jwks_cache['fetched'] = now
            return _clerk_jwks_cache['keys']
    except Exception:
        pass
    return None

def verify_clerk_token(session_token):
    """Verify a Clerk session JWT and return (clerk_user_id, email, name) or raise."""
    from jwt.algorithms import RSAAlgorithm
    import base64, json as _json

    # Decode header to get kid
    parts = session_token.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid token format')
    header = _json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
    kid = header.get('kid')

    keys = _get_clerk_jwks()
    if not keys:
        raise ValueError('Could not fetch Clerk JWKS')

    # Find matching key
    jwk = next((k for k in keys if k.get('kid') == kid), None)
    if not jwk:
        raise ValueError('No matching signing key found')

    public_key = RSAAlgorithm.from_jwk(json.dumps(jwk))
    payload = jwt.decode(
        session_token,
        public_key,
        algorithms=['RS256'],
        options={'verify_aud': False}
    )
    return payload  # contains 'sub' (clerk user id)

# ─── Database ────────────────────────────────────────────────────────────────

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA journal_mode=WAL')
        g.db.execute('PRAGMA foreign_keys=ON')
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id            TEXT PRIMARY KEY,
        email         TEXT UNIQUE NOT NULL,
        name          TEXT NOT NULL,
        password_hash TEXT NOT NULL DEFAULT '',
        avatar        TEXT DEFAULT '',
        clerk_id      TEXT DEFAULT '',
        settings      TEXT DEFAULT '{}',
        created_at    TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS transactions (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT NOT NULL,
        type        TEXT NOT NULL,
        amount      REAL NOT NULL,
        description TEXT NOT NULL,
        category    TEXT NOT NULL,
        date        TEXT NOT NULL,
        icon        TEXT DEFAULT '💳',
        payment     TEXT DEFAULT 'UPI',
        bank        TEXT DEFAULT '',
        tags        TEXT DEFAULT '',
        notes       TEXT DEFAULT '',
        recurring   INTEGER DEFAULT 0,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS budgets (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      TEXT NOT NULL,
        category     TEXT NOT NULL,
        limit_amount REAL NOT NULL,
        spent        REAL DEFAULT 0,
        icon         TEXT DEFAULT '💰',
        period       TEXT DEFAULT 'Monthly',
        alert        TEXT DEFAULT '90%',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS goals (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id  TEXT NOT NULL,
        name     TEXT NOT NULL,
        icon     TEXT DEFAULT '🎯',
        target   REAL NOT NULL,
        saved    REAL DEFAULT 0,
        deadline TEXT DEFAULT '',
        monthly  REAL DEFAULT 0,
        category TEXT DEFAULT '',
        notes    TEXT DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS investments (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id       TEXT NOT NULL,
        country       TEXT DEFAULT 'india',
        type          TEXT NOT NULL,
        name          TEXT NOT NULL,
        amount        REAL NOT NULL,
        current_value REAL NOT NULL,
        platform      TEXT DEFAULT '',
        start_date    TEXT DEFAULT '',
        notes         TEXT DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS banks (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    TEXT NOT NULL,
        name       TEXT NOT NULL,
        nickname   TEXT NOT NULL,
        type       TEXT DEFAULT 'Savings Account',
        balance    REAL DEFAULT 0,
        as_of      TEXT DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS cards (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id        TEXT NOT NULL,
        type           TEXT DEFAULT 'Credit Card',
        network        TEXT DEFAULT 'Visa',
        bank           TEXT NOT NULL,
        nickname       TEXT NOT NULL,
        last4          TEXT NOT NULL,
        expiry         TEXT NOT NULL,
        card_limit     REAL DEFAULT 0,
        outstanding    REAL DEFAULT 0,
        statement_day  INTEGER DEFAULT 1,
        due_day        INTEGER DEFAULT 20,
        min_pay        REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS subscriptions (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      TEXT NOT NULL,
        service      TEXT NOT NULL,
        category     TEXT DEFAULT 'Entertainment',
        amount       REAL NOT NULL,
        cycle        TEXT DEFAULT 'Monthly',
        start_date   TEXT DEFAULT '',
        next_renewal TEXT DEFAULT '',
        icon         TEXT DEFAULT '📱',
        payment      TEXT DEFAULT 'Credit Card',
        auto_renew   INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS lending (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT NOT NULL,
        type        TEXT NOT NULL,
        person      TEXT NOT NULL,
        amount      REAL NOT NULL,
        interest    REAL DEFAULT 0,
        mode        TEXT DEFAULT 'Cash',
        start_date  TEXT DEFAULT '',
        return_date TEXT DEFAULT '',
        status      TEXT DEFAULT 'pending',
        notes       TEXT DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    db.commit()
    db.close()

# ─── Auth Helpers ─────────────────────────────────────────────────────────────

def make_token(user_id):
    payload = {'sub': user_id, 'exp': datetime.utcnow() + timedelta(days=30)}
    return jwt.encode(payload, SECRET, algorithm='HS256')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth  = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            token = auth[7:]
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        try:
            data    = jwt.decode(token, SECRET, algorithms=['HS256'])
            user_id = data['sub']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Session expired, please sign in again'}), 401
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        db   = get_db()
        user = db.execute('SELECT * FROM users WHERE id=?', [user_id]).fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 401
        return f(user, *args, **kwargs)
    return decorated

def rows_to_list(db, sql, params=[]):
    return [dict(r) for r in db.execute(sql, params).fetchall()]

# ─── Clerk SSO Route ──────────────────────────────────────────────────────────

@app.route('/api/auth/clerk', methods=['POST'])
def clerk_auth():
    """Exchange a Clerk session token for a FinanceFlow JWT."""
    d = request.json or {}
    session_token = d.get('sessionToken', '')
    # Clerk also sends user info directly from the frontend SDK
    clerk_user_id = d.get('clerkUserId', '')
    email         = (d.get('email') or '').strip().lower()
    name          = (d.get('name') or 'User').strip()
    avatar        = d.get('avatar', '')

    if not clerk_user_id or not email:
        return jsonify({'error': 'Missing Clerk user data'}), 400

    # Verify the session token if secret key is configured
    if CLERK_SECRET and session_token:
        try:
            payload = verify_clerk_token(session_token)
            # Ensure the token's subject matches the declared user id
            if payload.get('sub') != clerk_user_id:
                return jsonify({'error': 'Token subject mismatch'}), 401
        except Exception as e:
            return jsonify({'error': f'Clerk token verification failed: {e}'}), 401

    db = get_db()

    # Check if we already have a user with this Clerk ID or email
    user = db.execute('SELECT * FROM users WHERE clerk_id=?', [clerk_user_id]).fetchone()
    is_new = False

    if not user:
        # Try to match by email (e.g. existing email/password user now using SSO)
        user = db.execute('SELECT * FROM users WHERE email=?', [email]).fetchone()
        if user:
            # Link Clerk ID to existing account
            db.execute('UPDATE users SET clerk_id=?, avatar=? WHERE id=?',
                       [clerk_user_id, avatar or user['avatar'], user['id']])
            db.commit()
            user = db.execute('SELECT * FROM users WHERE id=?', [user['id']]).fetchone()
        else:
            # Brand new user via Clerk
            user_id = str(uuid.uuid4())
            db.execute(
                'INSERT INTO users (id, email, name, password_hash, avatar, clerk_id) VALUES (?,?,?,?,?,?)',
                [user_id, email, name, '', avatar, clerk_user_id]
            )
            db.commit()
            user = db.execute('SELECT * FROM users WHERE id=?', [user_id]).fetchone()
            is_new = True

    token    = make_token(user['id'])
    settings = json.loads(user['settings'] or '{}')
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'], 'name': user['name'], 'email': user['email'],
            'avatar': user['avatar'], 'settings': settings, 'is_new': is_new
        }
    })

@app.route('/api/auth/clerk-config', methods=['GET'])
def clerk_config():
    """Return the Clerk publishable key so the frontend can load ClerkJS."""
    return jsonify({'publishableKey': CLERK_PUB_KEY})

# ─── Auth Routes ──────────────────────────────────────────────────────────────

@app.route('/api/auth/register', methods=['POST'])
def register():
    d        = request.json or {}
    email    = (d.get('email') or '').strip().lower()
    name     = (d.get('name') or '').strip()
    password = d.get('password') or ''
    if not email or not name or len(password) < 6:
        return jsonify({'error': 'Name, valid email, and password (6+ chars) required'}), 400
    db = get_db()
    if db.execute('SELECT id FROM users WHERE email=?', [email]).fetchone():
        return jsonify({'error': 'Email already registered. Please sign in.'}), 409
    user_id = str(uuid.uuid4())
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    db.execute('INSERT INTO users (id,email,name,password_hash) VALUES (?,?,?,?)',
               [user_id, email, name, pw_hash])
    db.commit()
    token = make_token(user_id)
    return jsonify({
        'token': token,
        'user': {'id': user_id, 'name': name, 'email': email, 'settings': {}, 'is_new': True}
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    d        = request.json or {}
    email    = (d.get('email') or '').strip().lower()
    password = d.get('password') or ''
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    db   = get_db()
    user = db.execute('SELECT * FROM users WHERE email=?', [email]).fetchone()
    if not user or not bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
        return jsonify({'error': 'Invalid email or password'}), 401
    token    = make_token(user['id'])
    settings = json.loads(user['settings'] or '{}')
    return jsonify({
        'token': token,
        'user': {'id': user['id'], 'name': user['name'], 'email': user['email'],
                 'avatar': user['avatar'], 'settings': settings}
    })

@app.route('/api/user', methods=['GET', 'PUT'])
@token_required
def user_profile(current_user):
    db = get_db()
    if request.method == 'GET':
        settings = json.loads(current_user['settings'] or '{}')
        return jsonify({'id': current_user['id'], 'name': current_user['name'],
                        'email': current_user['email'], 'avatar': current_user['avatar'],
                        'settings': settings})
    d       = request.json or {}
    updates = []
    values  = []
    if 'name' in d:
        updates.append('name=?'); values.append(d['name'])
    if 'avatar' in d:
        updates.append('avatar=?'); values.append(d['avatar'])
    if 'settings' in d:
        existing = json.loads(current_user['settings'] or '{}')
        existing.update(d['settings'])
        updates.append('settings=?'); values.append(json.dumps(existing))
    if updates:
        values.append(current_user['id'])
        db.execute(f"UPDATE users SET {','.join(updates)} WHERE id=?", values)
        db.commit()
    return jsonify({'ok': True})

# ─── All Data (single fetch for sync) ────────────────────────────────────────

@app.route('/api/data', methods=['GET'])
@token_required
def get_all_data(current_user):
    db  = get_db()
    uid = current_user['id']
    return jsonify({
        'transactions':  rows_to_list(db, 'SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC,id DESC', [uid]),
        'budgets':       rows_to_list(db, 'SELECT * FROM budgets WHERE user_id=?', [uid]),
        'goals':         rows_to_list(db, 'SELECT * FROM goals WHERE user_id=?', [uid]),
        'investments':   rows_to_list(db, 'SELECT * FROM investments WHERE user_id=?', [uid]),
        'banks':         rows_to_list(db, 'SELECT * FROM banks WHERE user_id=?', [uid]),
        'cards':         rows_to_list(db, 'SELECT * FROM cards WHERE user_id=?', [uid]),
        'subscriptions': rows_to_list(db, 'SELECT * FROM subscriptions WHERE user_id=?', [uid]),
        'lending':       rows_to_list(db, 'SELECT * FROM lending WHERE user_id=?', [uid]),
    })

# ─── Transactions ─────────────────────────────────────────────────────────────

@app.route('/api/transactions', methods=['GET', 'POST'])
@token_required
def transactions(current_user):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'GET':
        return jsonify(rows_to_list(db, 'SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC,id DESC', [uid]))
    d = request.json or {}
    cur = db.execute(
        'INSERT INTO transactions (user_id,type,amount,description,category,date,icon,payment,bank,tags,notes,recurring) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
        [uid, d['type'], float(d['amount']), d['description'], d['category'], d['date'],
         d.get('icon','💳'), d.get('payment','UPI'), d.get('bank',''),
         d.get('tags',''), d.get('notes',''), int(bool(d.get('recurring', False)))])
    db.commit()
    return jsonify({'id': cur.lastrowid, 'ok': True}), 201

@app.route('/api/transactions/<int:tid>', methods=['PUT', 'DELETE'])
@token_required
def transaction(current_user, tid):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'DELETE':
        db.execute('DELETE FROM transactions WHERE id=? AND user_id=?', [tid, uid])
        db.commit()
        return jsonify({'ok': True})
    d = request.json or {}
    db.execute(
        'UPDATE transactions SET type=?,amount=?,description=?,category=?,date=?,icon=?,payment=?,bank=?,tags=?,notes=?,recurring=? WHERE id=? AND user_id=?',
        [d['type'], float(d['amount']), d['description'], d['category'], d['date'],
         d.get('icon','💳'), d.get('payment','UPI'), d.get('bank',''),
         d.get('tags',''), d.get('notes',''), int(bool(d.get('recurring', False))), tid, uid])
    db.commit()
    return jsonify({'ok': True})

# ─── Budgets ──────────────────────────────────────────────────────────────────

@app.route('/api/budgets', methods=['GET', 'POST'])
@token_required
def budgets(current_user):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'GET':
        return jsonify(rows_to_list(db, 'SELECT * FROM budgets WHERE user_id=?', [uid]))
    d = request.json or {}
    cur = db.execute(
        'INSERT INTO budgets (user_id,category,limit_amount,spent,icon,period,alert) VALUES (?,?,?,?,?,?,?)',
        [uid, d['category'], float(d['limit_amount']), float(d.get('spent',0)),
         d.get('icon','💰'), d.get('period','Monthly'), d.get('alert','90%')])
    db.commit()
    return jsonify({'id': cur.lastrowid, 'ok': True}), 201

@app.route('/api/budgets/<int:bid>', methods=['PUT', 'DELETE'])
@token_required
def budget(current_user, bid):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'DELETE':
        db.execute('DELETE FROM budgets WHERE id=? AND user_id=?', [bid, uid])
        db.commit()
        return jsonify({'ok': True})
    d = request.json or {}
    db.execute(
        'UPDATE budgets SET category=?,limit_amount=?,spent=?,icon=?,period=?,alert=? WHERE id=? AND user_id=?',
        [d['category'], float(d['limit_amount']), float(d.get('spent',0)),
         d.get('icon','💰'), d.get('period','Monthly'), d.get('alert','90%'), bid, uid])
    db.commit()
    return jsonify({'ok': True})

# ─── Goals ────────────────────────────────────────────────────────────────────

@app.route('/api/goals', methods=['GET', 'POST'])
@token_required
def goals(current_user):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'GET':
        return jsonify(rows_to_list(db, 'SELECT * FROM goals WHERE user_id=?', [uid]))
    d = request.json or {}
    cur = db.execute(
        'INSERT INTO goals (user_id,name,icon,target,saved,deadline,monthly,category,notes) VALUES (?,?,?,?,?,?,?,?,?)',
        [uid, d['name'], d.get('icon','🎯'), float(d['target']), float(d.get('saved',0)),
         d.get('deadline',''), float(d.get('monthly',0)), d.get('category',''), d.get('notes','')])
    db.commit()
    return jsonify({'id': cur.lastrowid, 'ok': True}), 201

@app.route('/api/goals/<int:gid>', methods=['PUT', 'DELETE'])
@token_required
def goal(current_user, gid):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'DELETE':
        db.execute('DELETE FROM goals WHERE id=? AND user_id=?', [gid, uid])
        db.commit()
        return jsonify({'ok': True})
    d = request.json or {}
    db.execute(
        'UPDATE goals SET name=?,icon=?,target=?,saved=?,deadline=?,monthly=?,category=?,notes=? WHERE id=? AND user_id=?',
        [d['name'], d.get('icon','🎯'), float(d['target']), float(d.get('saved',0)),
         d.get('deadline',''), float(d.get('monthly',0)), d.get('category',''), d.get('notes',''), gid, uid])
    db.commit()
    return jsonify({'ok': True})

# ─── Investments ──────────────────────────────────────────────────────────────

@app.route('/api/investments', methods=['GET', 'POST'])
@token_required
def investments(current_user):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'GET':
        return jsonify(rows_to_list(db, 'SELECT * FROM investments WHERE user_id=?', [uid]))
    d = request.json or {}
    cur = db.execute(
        'INSERT INTO investments (user_id,country,type,name,amount,current_value,platform,start_date,notes) VALUES (?,?,?,?,?,?,?,?,?)',
        [uid, d.get('country','india'), d['type'], d['name'],
         float(d['amount']), float(d['current_value']),
         d.get('platform',''), d.get('start_date',''), d.get('notes','')])
    db.commit()
    return jsonify({'id': cur.lastrowid, 'ok': True}), 201

@app.route('/api/investments/<int:iid>', methods=['PUT', 'DELETE'])
@token_required
def investment(current_user, iid):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'DELETE':
        db.execute('DELETE FROM investments WHERE id=? AND user_id=?', [iid, uid])
        db.commit()
        return jsonify({'ok': True})
    d = request.json or {}
    db.execute(
        'UPDATE investments SET country=?,type=?,name=?,amount=?,current_value=?,platform=?,start_date=?,notes=? WHERE id=? AND user_id=?',
        [d.get('country','india'), d['type'], d['name'],
         float(d['amount']), float(d['current_value']),
         d.get('platform',''), d.get('start_date',''), d.get('notes',''), iid, uid])
    db.commit()
    return jsonify({'ok': True})

# ─── Banks ────────────────────────────────────────────────────────────────────

@app.route('/api/banks', methods=['GET', 'POST'])
@token_required
def banks(current_user):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'GET':
        return jsonify(rows_to_list(db, 'SELECT * FROM banks WHERE user_id=?', [uid]))
    d = request.json or {}
    cur = db.execute(
        'INSERT INTO banks (user_id,name,nickname,type,balance,as_of) VALUES (?,?,?,?,?,?)',
        [uid, d['name'], d.get('nickname', d['name']), d.get('type','Savings Account'),
         float(d.get('balance',0)), d.get('as_of','')])
    db.commit()
    return jsonify({'id': cur.lastrowid, 'ok': True}), 201

@app.route('/api/banks/<int:bid>', methods=['PUT', 'DELETE'])
@token_required
def bank(current_user, bid):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'DELETE':
        db.execute('DELETE FROM banks WHERE id=? AND user_id=?', [bid, uid])
        db.commit()
        return jsonify({'ok': True})
    d = request.json or {}
    db.execute(
        'UPDATE banks SET name=?,nickname=?,type=?,balance=?,as_of=? WHERE id=? AND user_id=?',
        [d['name'], d.get('nickname',d['name']), d.get('type','Savings Account'),
         float(d.get('balance',0)), d.get('as_of',''), bid, uid])
    db.commit()
    return jsonify({'ok': True})

# ─── Cards ────────────────────────────────────────────────────────────────────

@app.route('/api/cards', methods=['GET', 'POST'])
@token_required
def cards(current_user):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'GET':
        return jsonify(rows_to_list(db, 'SELECT * FROM cards WHERE user_id=?', [uid]))
    d = request.json or {}
    cur = db.execute(
        'INSERT INTO cards (user_id,type,network,bank,nickname,last4,expiry,card_limit,outstanding,statement_day,due_day,min_pay) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
        [uid, d.get('type','Credit Card'), d.get('network','Visa'), d['bank'], d['nickname'],
         d['last4'], d['expiry'], float(d.get('card_limit',0)), float(d.get('outstanding',0)),
         int(d.get('statement_day',1)), int(d.get('due_day',20)), float(d.get('min_pay',0))])
    db.commit()
    return jsonify({'id': cur.lastrowid, 'ok': True}), 201

@app.route('/api/cards/<int:cid>', methods=['PUT', 'DELETE'])
@token_required
def card(current_user, cid):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'DELETE':
        db.execute('DELETE FROM cards WHERE id=? AND user_id=?', [cid, uid])
        db.commit()
        return jsonify({'ok': True})
    d = request.json or {}
    db.execute(
        'UPDATE cards SET type=?,network=?,bank=?,nickname=?,last4=?,expiry=?,card_limit=?,outstanding=?,statement_day=?,due_day=?,min_pay=? WHERE id=? AND user_id=?',
        [d.get('type','Credit Card'), d.get('network','Visa'), d['bank'], d['nickname'],
         d['last4'], d['expiry'], float(d.get('card_limit',0)), float(d.get('outstanding',0)),
         int(d.get('statement_day',1)), int(d.get('due_day',20)), float(d.get('min_pay',0)), cid, uid])
    db.commit()
    return jsonify({'ok': True})

# ─── Subscriptions ────────────────────────────────────────────────────────────

@app.route('/api/subscriptions', methods=['GET', 'POST'])
@token_required
def subscriptions(current_user):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'GET':
        return jsonify(rows_to_list(db, 'SELECT * FROM subscriptions WHERE user_id=?', [uid]))
    d = request.json or {}
    cur = db.execute(
        'INSERT INTO subscriptions (user_id,service,category,amount,cycle,start_date,next_renewal,icon,payment,auto_renew) VALUES (?,?,?,?,?,?,?,?,?,?)',
        [uid, d['service'], d.get('category','Entertainment'), float(d['amount']),
         d.get('cycle','Monthly'), d.get('start_date',''), d.get('next_renewal',''),
         d.get('icon','📱'), d.get('payment','Credit Card'), int(bool(d.get('auto_renew',True)))])
    db.commit()
    return jsonify({'id': cur.lastrowid, 'ok': True}), 201

@app.route('/api/subscriptions/<int:sid>', methods=['PUT', 'DELETE'])
@token_required
def subscription(current_user, sid):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'DELETE':
        db.execute('DELETE FROM subscriptions WHERE id=? AND user_id=?', [sid, uid])
        db.commit()
        return jsonify({'ok': True})
    d = request.json or {}
    db.execute(
        'UPDATE subscriptions SET service=?,category=?,amount=?,cycle=?,start_date=?,next_renewal=?,icon=?,payment=?,auto_renew=? WHERE id=? AND user_id=?',
        [d['service'], d.get('category','Entertainment'), float(d['amount']),
         d.get('cycle','Monthly'), d.get('start_date',''), d.get('next_renewal',''),
         d.get('icon','📱'), d.get('payment','Credit Card'), int(bool(d.get('auto_renew',True))), sid, uid])
    db.commit()
    return jsonify({'ok': True})

# ─── Lending ──────────────────────────────────────────────────────────────────

@app.route('/api/lending', methods=['GET', 'POST'])
@token_required
def lending_list(current_user):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'GET':
        return jsonify(rows_to_list(db, 'SELECT * FROM lending WHERE user_id=?', [uid]))
    d = request.json or {}
    cur = db.execute(
        'INSERT INTO lending (user_id,type,person,amount,interest,mode,start_date,return_date,status,notes) VALUES (?,?,?,?,?,?,?,?,?,?)',
        [uid, d['type'], d['person'], float(d['amount']), float(d.get('interest',0)),
         d.get('mode','Cash'), d.get('start_date',''), d.get('return_date',''),
         d.get('status','pending'), d.get('notes','')])
    db.commit()
    return jsonify({'id': cur.lastrowid, 'ok': True}), 201

@app.route('/api/lending/<int:lid>', methods=['PUT', 'DELETE'])
@token_required
def lending_item(current_user, lid):
    db  = get_db()
    uid = current_user['id']
    if request.method == 'DELETE':
        db.execute('DELETE FROM lending WHERE id=? AND user_id=?', [lid, uid])
        db.commit()
        return jsonify({'ok': True})
    d = request.json or {}
    db.execute(
        'UPDATE lending SET type=?,person=?,amount=?,interest=?,mode=?,start_date=?,return_date=?,status=?,notes=? WHERE id=? AND user_id=?',
        [d['type'], d['person'], float(d['amount']), float(d.get('interest',0)),
         d.get('mode','Cash'), d.get('start_date',''), d.get('return_date',''),
         d.get('status','pending'), d.get('notes',''), lid, uid])
    db.commit()
    return jsonify({'ok': True})

# ─── Market Data Proxy ────────────────────────────────────────────────────────

@app.route('/api/market/quotes')
def market_quotes():
    """Proxy Yahoo Finance to avoid browser CORS blocks."""
    symbols_raw = request.args.get('symbols', '')
    symbols     = [s.strip() for s in symbols_raw.split(',') if s.strip()][:30]
    results     = {}
    for sym in symbols:
        try:
            url  = f'https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1d&range=1d'
            r    = requests.get(url, headers=MKT_HEADERS, timeout=7)
            meta = r.json()['chart']['result'][0]['meta']
            prev  = meta.get('chartPreviousClose') or meta.get('previousClose') or meta['regularMarketPrice']
            price = meta['regularMarketPrice']
            chg   = round((price - prev) / prev * 100, 2) if prev else 0.0
            results[sym] = {
                'price':    price,
                'change':   chg,
                'prev':     prev,
                'currency': meta.get('currency', 'INR'),
                'name':     meta.get('shortName', sym)
            }
        except Exception:
            results[sym] = None
    return jsonify(results)

@app.route('/api/market/crypto')
def market_crypto():
    """Proxy CoinGecko for crypto prices."""
    try:
        r = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=inr,usd',
            headers=MKT_HEADERS, timeout=8)
        return jsonify(r.json())
    except Exception:
        return jsonify({})

# ─── Frontend ─────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/<path:path>')
def static_files(path):
    try:
        return send_file(path)
    except Exception:
        return send_file('index.html')

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print(f'FinanceFlow server starting on port {port}')
    app.run(host='0.0.0.0', port=port, debug=False)
