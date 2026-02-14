from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import json
import os
import random
from functools import wraps

app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Debug info
print("=" * 60)
print("SPENDY - DEBUG INFO")
print("=" * 60)
print(f"Static folder: {app.static_folder}")
print(f"Template folder: {app.template_folder}")
css_path = os.path.join(app.static_folder, 'css', 'style.css')
print(f"CSS file exists: {os.path.exists(css_path)}")
print("=" * 60)

# File-based storage — use /tmp for writable storage on Render
DATA_FILE = os.environ.get('DATA_FILE', '/tmp/user_data.json')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'budget': {
            'monthly': 0,
            'weekly': 0,
            'category': {}
        },
        'spent': 0,
        'transactions': [],
        'trusted_contacts': [],
        'lock_status': {
            'locked': False,
            'locked_at': None,
            'unlock_requests': []
        },
        'emergency_requests': [],  # Pending emergency transaction requests
        'streak': {
            'current': 0,
            'best': 0,
            'last_check': None
        },
        'upi_contacts': [],  # Recent UPI contacts
        'balance': 10000.0  # Simulated wallet balance
    }
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['user_id'] = 'demo_user'
        return f(*args, **kwargs)
    return decorated_function

def generate_upi_ref():
    """Generate a realistic UPI reference number"""
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"UPI{timestamp}{random_part}"

@app.route('/')
@login_required
def index():
    data = load_data()
    
    # Calculate daily safe spend
    today = datetime.now()
    days_in_month = (datetime(today.year, today.month + 1 if today.month < 12 else 1, 1) - timedelta(days=1)).day
    days_remaining = days_in_month - today.day + 1
    
    monthly_budget = data['budget']['monthly']
    spent = data['spent']
    remaining = monthly_budget - spent
    daily_safe_spend = remaining / days_remaining if days_remaining > 0 else 0
    
    # Calculate spending rate warning
    days_passed = today.day
    avg_daily_spend = spent / days_passed if days_passed > 0 else 0
    days_until_broke = remaining / avg_daily_spend if avg_daily_spend > 0 else float('inf')
    
    # Check if 70% spent before mid-month
    warning = False
    if days_passed < 15 and spent >= (monthly_budget * 0.7):
        warning = True
    
    stats = {
        'monthly_budget': monthly_budget,
        'spent': spent,
        'remaining': remaining,
        'daily_safe_spend': daily_safe_spend,
        'days_remaining': days_remaining,
        'days_until_broke': days_until_broke,
        'warning': warning,
        'percent_spent': (spent / monthly_budget * 100) if monthly_budget > 0 else 0,
        'balance': data.get('balance', 10000.0)
    }
    
    return render_template('index.html', 
                         data=data, 
                         stats=stats,
                         transactions=data['transactions'][-10:])

@app.route('/setup-budget', methods=['GET', 'POST'])
@login_required
def setup_budget():
    if request.method == 'POST':
        data = load_data()
        
        budget_type = request.form.get('budget_type')
        amount = float(request.form.get('amount', 0))
        
        if budget_type == 'monthly':
            data['budget']['monthly'] = amount
            data['budget']['weekly'] = amount / 4.33
        elif budget_type == 'weekly':
            data['budget']['weekly'] = amount
            data['budget']['monthly'] = amount * 4.33
        
        save_data(data)
        return redirect(url_for('index'))
    
    return render_template('setup_budget.html')

@app.route('/add-transaction', methods=['POST'])
@login_required
def add_transaction():
    data = load_data()
    
    # Check if locked
    if data['lock_status']['locked']:
        locked_at = datetime.fromisoformat(data['lock_status']['locked_at'])
        if datetime.now() - locked_at < timedelta(hours=24):
            return jsonify({
                'success': False,
                'error': 'Account locked. Wait 24 hours or get trusted contact approval.'
            })
        else:
            data['lock_status']['locked'] = False
            data['lock_status']['locked_at'] = None
    
    transaction_data = request.json
    amount = float(transaction_data.get('amount', 0))
    category = transaction_data.get('category', 'Other')
    description = transaction_data.get('description', '')
    
    transaction = {
        'id': len(data['transactions']) + 1,
        'amount': amount,
        'category': category,
        'description': description,
        'timestamp': datetime.now().isoformat(),
        'type': 'expense'
    }
    
    data['transactions'].append(transaction)
    data['spent'] += amount
    
    # Check if limit reached
    if data['spent'] >= data['budget']['monthly']:
        data['lock_status']['locked'] = True
        data['lock_status']['locked_at'] = datetime.now().isoformat()
    
    save_data(data)
    
    return jsonify({
        'success': True,
        'locked': data['lock_status']['locked'],
        'spent': data['spent'],
        'remaining': data['budget']['monthly'] - data['spent']
    })

@app.route('/upi-pay')
@login_required
def upi_pay():
    """Main UPI payment interface - simulated like PhonePe/GPay"""
    data = load_data()
    return render_template('upi_pay.html', 
                         balance=data.get('balance', 10000.0),
                         recent_contacts=data.get('upi_contacts', [])[-5:])

@app.route('/upi-send', methods=['POST'])
@login_required
def upi_send():
    """Process UPI payment"""
    data = load_data()
    
    # Check if locked
    if data['lock_status']['locked']:
        return jsonify({
            'success': False,
            'error': 'Account locked. Cannot make payment.'
        })
    
    payment_data = request.json
    amount = float(payment_data.get('amount', 0))
    upi_id = payment_data.get('upi_id', '')
    note = payment_data.get('note', '')
    recipient_name = payment_data.get('recipient_name', upi_id.split('@')[0])
    
    # Check balance
    current_balance = data.get('balance', 10000.0)
    if amount > current_balance:
        return jsonify({
            'success': False,
            'error': 'Insufficient balance'
        })
    
    # Generate UPI reference
    upi_ref = generate_upi_ref()
    
    # Create transaction
    transaction = {
        'id': len(data['transactions']) + 1,
        'amount': amount,
        'category': 'UPI Payment',
        'description': f'Paid to {recipient_name}' + (f': {note}' if note else ''),
        'timestamp': datetime.now().isoformat(),
        'type': 'upi_payment',
        'upi_id': upi_id,
        'upi_ref': upi_ref,
        'recipient_name': recipient_name,
        'status': 'success'
    }
    
    # Update data
    data['transactions'].append(transaction)
    data['spent'] += amount
    data['balance'] = current_balance - amount
    
    # Add to recent contacts if not exists
    if not any(c.get('upi_id') == upi_id for c in data.get('upi_contacts', [])):
        data.setdefault('upi_contacts', []).append({
            'upi_id': upi_id,
            'name': recipient_name,
            'last_paid': datetime.now().isoformat()
        })
    
    # Check if budget limit reached
    if data['spent'] >= data['budget']['monthly']:
        data['lock_status']['locked'] = True
        data['lock_status']['locked_at'] = datetime.now().isoformat()
    
    save_data(data)
    
    return jsonify({
        'success': True,
        'message': 'Payment successful',
        'upi_ref': upi_ref,
        'transaction_id': transaction['id'],
        'locked': data['lock_status']['locked'],
        'new_balance': data['balance']
    })

@app.route('/upi-verify', methods=['POST'])
@login_required
def upi_verify():
    """Verify UPI ID (simulated)"""
    upi_id = request.json.get('upi_id', '')
    
    # Simulate verification (in real app, this would check with payment gateway)
    if '@' not in upi_id:
        return jsonify({
            'valid': False,
            'error': 'Invalid UPI ID format'
        })
    
    # Generate a name based on UPI ID
    username = upi_id.split('@')[0]
    provider = upi_id.split('@')[1] if '@' in upi_id else ''
    
    # Simulate some UPI IDs as invalid
    if username in ['invalid', 'test123', 'notfound']:
        return jsonify({
            'valid': False,
            'error': 'UPI ID not found'
        })
    
    return jsonify({
        'valid': True,
        'name': username.title().replace('.', ' ').replace('_', ' '),
        'provider': provider
    })

@app.route('/scan-qr')
@login_required
def scan_qr():
    """QR code scanner interface"""
    return render_template('scan_qr.html')

@app.route('/trusted-contacts', methods=['GET', 'POST'])
@login_required
def trusted_contacts():
    data = load_data()
    
    if request.method == 'POST':
        contact_data = request.json
        
        if contact_data.get('action') == 'add':
            contact = {
                'id': len(data['trusted_contacts']) + 1,
                'name': contact_data.get('name'),
                'phone': contact_data.get('phone'),
                'email': contact_data.get('email')
            }
            data['trusted_contacts'].append(contact)
            save_data(data)
            return jsonify({'success': True})
        
        elif contact_data.get('action') == 'request_unlock':
            request_obj = {
                'id': len(data['lock_status']['unlock_requests']) + 1,
                'requested_at': datetime.now().isoformat(),
                'status': 'pending'
            }
            data['lock_status']['unlock_requests'].append(request_obj)
            save_data(data)
            return jsonify({'success': True, 'message': 'Unlock request sent to trusted contacts'})
        
        elif contact_data.get('action') == 'approve_unlock':
            data['lock_status']['locked'] = False
            data['lock_status']['locked_at'] = None
            data['lock_status']['unlock_requests'] = []
            save_data(data)
            return jsonify({'success': True, 'message': 'Account unlocked'})
    
    return render_template('trusted_contacts.html', contacts=data['trusted_contacts'])

@app.route('/streak')
@login_required
def streak():
    data = load_data()
    
    today = datetime.now()
    monthly_budget = data['budget']['monthly']
    spent = data['spent']
    
    saved_amount = monthly_budget - spent if spent < monthly_budget else 0
    under_budget = spent < monthly_budget
    
    if data['streak']['last_check']:
        last_check = datetime.fromisoformat(data['streak']['last_check'])
        if last_check.month != today.month and under_budget:
            data['streak']['current'] += 1
            if data['streak']['current'] > data['streak']['best']:
                data['streak']['best'] = data['streak']['current']
        elif last_check.month != today.month and not under_budget:
            data['streak']['current'] = 0
    
    data['streak']['last_check'] = today.isoformat()
    save_data(data)
    
    rewards = []
    if data['streak']['current'] >= 1:
        rewards.append({'title': '🏆 Budget Master', 'description': '1 month streak'})
    if data['streak']['current'] >= 3:
        rewards.append({'title': '💎 Diamond Saver', 'description': '3 month streak', 'reward': '₹100 cashback'})
    if data['streak']['current'] >= 6:
        rewards.append({'title': '👑 Financial Wizard', 'description': '6 month streak', 'reward': '₹500 cashback'})
    if data['streak']['current'] >= 12:
        rewards.append({'title': '🌟 Legendary', 'description': '1 year streak', 'reward': '₹2000 cashback'})
    
    return render_template('streak.html', 
                         streak=data['streak'], 
                         saved_amount=saved_amount,
                         rewards=rewards)

@app.route('/analytics')
@login_required
def analytics():
    data = load_data()
    
    category_totals = {}
    for transaction in data['transactions']:
        category = transaction.get('category', 'Other')
        category_totals[category] = category_totals.get(category, 0) + transaction['amount']
    
    daily_spending = {}
    for transaction in data['transactions']:
        date = datetime.fromisoformat(transaction['timestamp']).date().isoformat()
        daily_spending[date] = daily_spending.get(date, 0) + transaction['amount']
    
    # Calculate financial summary
    monthly_budget = data['budget']['monthly']
    total_spent = data['spent']
    wallet_balance = data.get('balance', 10000.0)
    total_income = wallet_balance + total_spent  # Simulated total income
    
    return render_template('analytics.html', 
                         category_totals=category_totals,
                         daily_spending=daily_spending,
                         data=data,
                         wallet_balance=wallet_balance,
                         total_spent=total_spent,
                         monthly_budget=monthly_budget,
                         total_income=total_income)

@app.route('/api/status')
@login_required
def api_status():
    data = load_data()
    today = datetime.now()
    days_in_month = (datetime(today.year, today.month + 1 if today.month < 12 else 1, 1) - timedelta(days=1)).day
    days_remaining = days_in_month - today.day + 1
    
    monthly_budget = data['budget']['monthly']
    spent = data['spent']
    remaining = monthly_budget - spent
    daily_safe_spend = remaining / days_remaining if days_remaining > 0 else 0
    
    return jsonify({
        'budget': monthly_budget,
        'spent': spent,
        'remaining': remaining,
        'daily_safe_spend': daily_safe_spend,
        'locked': data['lock_status']['locked'],
        'streak': data['streak']['current'],
        'balance': data.get('balance', 10000.0)
    })

@app.route('/emergency-approvals')
@login_required
def emergency_approvals():
    """Emergency transaction approval page"""
    data = load_data()
    
    # Ensure emergency_requests exists
    if 'emergency_requests' not in data:
        data['emergency_requests'] = []
        save_data(data)
    
    # Get pending requests
    pending_requests = [r for r in data.get('emergency_requests', []) if r.get('status') == 'pending']
    
    return render_template('emergency_approvals.html', 
                         contacts=data['trusted_contacts'],
                         pending_requests=pending_requests,
                         locked=data['lock_status']['locked'])

@app.route('/request-emergency-transaction', methods=['POST'])
@login_required
def request_emergency_transaction():
    """Request emergency transaction when account is locked"""
    data = load_data()
    
    # Get request data properly
    try:
        request_data = request.get_json()
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Invalid request data'
        })
    
    # Check if account is locked
    if not data['lock_status']['locked']:
        return jsonify({
            'success': False,
            'error': 'Account is not locked. Regular transactions available.'
        })
    
    # Check if user has trusted contacts
    if not data.get('trusted_contacts') or len(data['trusted_contacts']) == 0:
        return jsonify({
            'success': False,
            'error': 'Please add trusted contacts first to use emergency transactions.'
        })
    
    amount = float(request_data.get('amount', 0))
    upi_id = request_data.get('upi_id', '')
    note = request_data.get('note', '')
    recipient_name = request_data.get('recipient_name', upi_id.split('@')[0])
    
    # Validate amount
    if amount <= 0:
        return jsonify({
            'success': False,
            'error': 'Invalid amount'
        })
    
    # Check balance
    current_balance = data.get('balance', 10000.0)
    if amount > current_balance:
        return jsonify({
            'success': False,
            'error': 'Insufficient balance'
        })
    
    # Create emergency request
    emergency_request = {
        'id': len(data.get('emergency_requests', [])) + 1,
        'amount': amount,
        'upi_id': upi_id,
        'recipient_name': recipient_name,
        'note': note,
        'requested_at': datetime.now().isoformat(),
        'status': 'pending',
        'approved_by': None
    }
    
    if 'emergency_requests' not in data:
        data['emergency_requests'] = []
    data['emergency_requests'].append(emergency_request)
    
    save_data(data)
    
    return jsonify({
        'success': True,
        'message': 'Emergency transaction request sent to your trusted contacts for approval.',
        'request_id': emergency_request['id']
    })

@app.route('/approve-emergency-transaction', methods=['POST'])
@login_required
def approve_emergency_transaction():
    """Approve an emergency transaction (simulates trusted contact approval)"""
    data = load_data()
    approval_data = request.json
    
    request_id = approval_data.get('request_id')
    contact_name = approval_data.get('contact_name', 'Trusted Contact')
    
    # Find the request
    emergency_request = None
    for req in data.get('emergency_requests', []):
        if req['id'] == request_id and req['status'] == 'pending':
            emergency_request = req
            break
    
    if not emergency_request:
        return jsonify({
            'success': False,
            'error': 'Request not found or already processed'
        })
    
    # Check balance again
    current_balance = data.get('balance', 10000.0)
    if emergency_request['amount'] > current_balance:
        emergency_request['status'] = 'rejected'
        emergency_request['rejection_reason'] = 'Insufficient balance'
        save_data(data)
        return jsonify({
            'success': False,
            'error': 'Insufficient balance'
        })
    
    # Generate UPI reference
    upi_ref = generate_upi_ref()
    
    # Process the payment
    transaction = {
        'id': len(data['transactions']) + 1,
        'amount': emergency_request['amount'],
        'category': 'Emergency Payment',
        'description': f"Emergency payment to {emergency_request['recipient_name']} (Approved by {contact_name})" + (f": {emergency_request['note']}" if emergency_request['note'] else ''),
        'timestamp': datetime.now().isoformat(),
        'type': 'emergency_upi',
        'upi_id': emergency_request['upi_id'],
        'upi_ref': upi_ref,
        'recipient_name': emergency_request['recipient_name'],
        'status': 'success',
        'approved_by': contact_name
    }
    
    data['transactions'].append(transaction)
    data['spent'] += emergency_request['amount']
    data['balance'] = current_balance - emergency_request['amount']
    
    # Update request status
    emergency_request['status'] = 'approved'
    emergency_request['approved_by'] = contact_name
    emergency_request['approved_at'] = datetime.now().isoformat()
    emergency_request['upi_ref'] = upi_ref
    
    save_data(data)
    
    return jsonify({
        'success': True,
        'message': f'Emergency transaction approved by {contact_name}!',
        'upi_ref': upi_ref,
        'new_balance': data['balance']
    })

@app.route('/reject-emergency-transaction', methods=['POST'])
@login_required
def reject_emergency_transaction():
    """Reject an emergency transaction"""
    data = load_data()
    rejection_data = request.json
    
    request_id = rejection_data.get('request_id')
    reason = rejection_data.get('reason', 'Not approved')
    
    # Find the request
    for req in data.get('emergency_requests', []):
        if req['id'] == request_id and req['status'] == 'pending':
            req['status'] = 'rejected'
            req['rejection_reason'] = reason
            req['rejected_at'] = datetime.now().isoformat()
            save_data(data)
            return jsonify({
                'success': True,
                'message': 'Emergency transaction rejected'
            })
    
    return jsonify({
        'success': False,
        'error': 'Request not found or already processed'
    })

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("SPENDY - Ready!")
    print("Open: http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
