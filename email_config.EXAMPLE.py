# ══════════════════════════════════════════════════
#  Fancy فانسي — Email Configuration
#  
#  HOW TO SETUP:
#  1. Rename this file to: email_config.py
#  2. Fill in your Gmail address and App Password
#  3. Restart the server (2_RUN.bat)
#
#  HOW TO GET GMAIL APP PASSWORD:
#  1. Go to: myaccount.google.com/security
#  2. Enable "2-Step Verification"
#  3. Go to: myaccount.google.com/apppasswords
#  4. App name: "Fancy Store" → Click Create
#  5. Copy the 16-character password (e.g. abcd efgh ijkl mnop)
#  6. Paste it below WITHOUT spaces
# ══════════════════════════════════════════════════

EMAIL_BACKEND    = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST       = 'smtp.gmail.com'
EMAIL_PORT       = 587
EMAIL_USE_TLS    = True
EMAIL_HOST_USER  = 'your-gmail@gmail.com'      # ← ضع إيميلك هنا
EMAIL_HOST_PASSWORD = 'abcdefghijklmnop'        # ← ضع App Password هنا (16 حرف بدون مسافات)
DEFAULT_FROM_EMAIL = 'Fancy فانسي <your-gmail@gmail.com>'
