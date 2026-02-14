## Team Name - Elytra
# Group Members
1. Crystal Maria Biju - Jain University,Kochi
2. Akshaya Shinoy - Jain University,Kochi
# 💰 Spendy - Budget Tracker with Built-in UPI

A modern Flask-based budget tracking app with **simulated UPI payment functionality** built right in!

## ✨ What's New

### 🎯 Built-in UPI Payment Simulation
- **No external apps needed** - Make UPI payments directly in the app
- **Real-time UPI ID verification** - Validates UPI IDs before payment
- **Simulated wallet balance** - Track payments from your virtual wallet
- **UPI reference numbers** - Generate realistic transaction IDs
- **Recent contacts** - Quick pay to recent recipients
- **QR code scanner** - Simulated QR scanning for merchant payments

### 🎨 Enhanced Features
- **Darker category dropdown** - Fixed visibility issue with white text on dropdown options
- **Modern UPI interface** - Looks like PhonePe/GPay with glassmorphic design
- **Success animations** - Smooth payment confirmation screens
- **Quick amount buttons** - Fast payment with preset amounts

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the App

**On Mac/Linux:**
```bash
./start.sh
```

**On Windows:**
```
START.bat
```

**Or directly:**
```bash
python app.py
```

### 3. Open in Browser
```
http://localhost:5000
```

## 📱 How to Use

### Setup Your Budget
1. Click "Set Up Budget" on first visit
2. Choose monthly or weekly budget
3. Enter your amount (e.g., ₹5000)
4. Click "Save Budget & Continue"

### Make UPI Payments (Simulated)
1. Click **"💳 Pay"** in the navigation
2. You'll see your wallet balance (starts at ₹10,000)
3. Enter a UPI ID (e.g., `friend@paytm`)
   - The app will verify it (simulated)
   - You'll see the recipient's name
4. Enter amount or use quick buttons (₹100, ₹500, ₹1000, etc.)
5. Add a note (optional)
6. Click **"Pay Now"**
7. Success screen shows:
   - Payment confirmation
   - UPI reference ID
   - Transaction details
   - Updated balance

### Scan QR Codes
1. Click **"📷 Scan QR Code to Pay"**
2. Click **"Simulate QR Scan"**
3. App simulates scanning a merchant QR
4. Auto-fills payment form with merchant details

### Track Expenses
1. Click **"+ Add Expense"** on dashboard
2. Enter amount
3. **Select category** from dropdown (now with visible dark text!)
4. Add description
5. Click "Add Expense"

## 🎨 Category Dropdown Fix

The category dropdown now has **much darker, more visible text**:

```css
/* Before: Light gray text (hard to read) */
select option { color: #9BA3AF; }

/* After: White text on dark background */
select option {
    background: #1A1F36;  /* Dark background */
    color: #FFFFFF;        /* White text */
    font-weight: 600;      /* Bold for better visibility */
}
```

## 💡 Features Breakdown

### Dashboard
- Monthly budget overview
- Remaining balance
- Daily safe spend calculation
- Current streak display
- Recent transactions list
- Quick action buttons

### UPI Payment Interface
- Simulated wallet balance
- Real-time UPI ID verification
- Quick amount selection
- Payment notes
- Recent contacts for quick pay
- Success screen with transaction details

### Budget Tracking
- Hard lock when limit reached
- Smart spending alerts at 70% usage
- Daily safe spend recommendations
- Budget vs actual tracking

### Savings Streak
- Monthly streak counter
- Rewards at milestones:
  - 🏆 1 month: Budget Master
  - 💎 3 months: Diamond Saver - ₹100
  - 👑 6 months: Financial Wizard - ₹500
  - 🌟 12 months: Legendary - ₹2000

### Analytics
- Category-wise spending breakdown
- Daily spending trends
- Transaction history

## 🎯 How the UPI Simulation Works

### Backend (`app.py`)
```python
@app.route('/upi-send', methods=['POST'])
def upi_send():
    # Check account not locked
    # Verify sufficient balance
    # Generate UPI reference number
    # Create transaction record
    # Update wallet balance
    # Check if budget limit reached
    # Return success with details
```

### Frontend (UPI verification)
```javascript
// Real-time UPI ID verification
document.getElementById('upi-id').addEventListener('input', async function() {
    const upiId = this.value;
    
    // Debounce for better UX
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
        const response = await fetch('/upi-verify', {
            method: 'POST',
            body: JSON.stringify({upi_id: upiId})
        });
        
        const data = await response.json();
        // Show verified name or error
    }, 500);
});
```

### UPI Reference Generation
```python
def generate_upi_ref():
    """Generate realistic UPI reference like: UPI240214153045123456"""
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    random_part = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return f"UPI{timestamp}{random_part}"
```

## 🔧 Technical Details

### File Structure
```
smartbudget_upi/
├── app.py                     # Main Flask application with UPI logic
├── requirements.txt           # Python dependencies
├── start.sh / START.bat       # Startup scripts
├── static/
│   ├── css/
│   │   └── style.css         # Enhanced CSS with dropdown fix
│   └── js/
│       └── main.js           # Frontend JavaScript
└── templates/
    ├── base.html             # Base template
    ├── index.html            # Dashboard
    ├── upi_pay.html          # UPI payment interface ⭐ NEW
    ├── scan_qr.html          # QR scanner ⭐ NEW
    ├── setup_budget.html     # Budget setup
    ├── trusted_contacts.html # Trusted contacts
    ├── streak.html           # Savings streak
    └── analytics.html        # Analytics

```

### Data Storage (JSON)
```json
{
  "budget": {"monthly": 5000, "weekly": 1154},
  "spent": 1200,
  "balance": 8800,          // ⭐ NEW: Wallet balance
  "transactions": [
    {
      "id": 1,
      "amount": 500,
      "category": "UPI Payment",
      "type": "upi_payment",  // ⭐ NEW: Payment type
      "upi_id": "friend@paytm",
      "upi_ref": "UPI240214...",
      "recipient_name": "Friend",
      "status": "success"
    }
  ],
  "upi_contacts": [          // ⭐ NEW: Recent contacts
    {
      "upi_id": "friend@paytm",
      "name": "Friend",
      "last_paid": "2024-02-14T15:30:00"
    }
  ]
}
```

## 🎨 Design Highlights

### UPI Payment Interface
- **Balance Card**: Purple gradient showing wallet balance
- **Payment Form**: Glass card with input fields
- **Quick Amounts**: Grid of preset payment amounts
- **Real-time Verification**: Green checkmark when UPI ID is valid
- **Success Animation**: Animated checkmark on successful payment

### Category Dropdown Enhancement
- Background: Dark navy (#1A1F36)
- Text: Pure white (#FFFFFF)
- Font weight: 600 (semi-bold)
- Much more readable than before!

## 📱 Mobile Responsive

All UPI features are fully responsive:
- Touch-friendly buttons
- Optimized input fields
- Stack layout on mobile
- Large tap targets

## ⚠️ Important Notes

### This is a Simulation
- UPI payments are **simulated** for demo purposes
- No real money is transferred
- No connection to actual UPI infrastructure
- Great for learning, prototyping, or demo purposes

### For Production Use
To make this a real UPI app, you would need:
1. **UPI Payment Gateway Integration**
   - Razorpay UPI
   - PayU
   - Cashfree
   - PhonePe Business

2. **KYC Compliance**
   - User verification
   - Bank account linking
   - RBI compliance

3. **Security**
   - SSL/HTTPS
   - PCI DSS compliance
   - Secure payment tokens
   - 2FA authentication

4. **Database**
   - PostgreSQL/MySQL
   - Proper transaction logging
   - Backup and recovery

## 🚀 Next Steps

Want to enhance this further?

1. **Add more payment methods**
   - Credit/Debit cards
   - Net banking
   - Wallets

2. **Bill splitting**
   - Split payments with friends
   - Request money feature

3. **Recurring payments**
   - Set up automatic UPI payments
   - Subscription tracking

4. **Payment reminders**
   - Due date notifications
   - Bill payment reminders

## 🐛 Troubleshooting

### Dropdown text still not visible?
Hard refresh your browser:
- **Windows**: `Ctrl + Shift + R`
- **Mac**: `Cmd + Shift + R`
- Or use Incognito mode

### UPI verification not working?
Check browser console for errors. The verification is instant - if you enter a valid UPI format (`name@provider`), it should verify immediately.

### Balance not updating?
Refresh the page after payment. The success screen shows updated balance automatically.

## 📄 License

Open source - Use freely for personal or educational purposes!

---

**Enjoy your new UPI-powered budget tracker!** 💳✨
