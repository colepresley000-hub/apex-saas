"""
GUMROAD INTEGRATION
Handle payments and license key verification
"""
import requests
import sqlite3
from datetime import datetime

class GumroadIntegration:
    """
    Integrates with Gumroad for payments
    Verifies license keys and manages subscriptions
    """
    
    def __init__(self, product_permalink):
        self.product_permalink = product_permalink
        self.verify_url = "https://api.gumroad.com/v2/licenses/verify"
    
    def verify_license(self, license_key: str, email: str = None):
        """Verify a Gumroad license key"""
        payload = {
            'product_permalink': self.product_permalink,
            'license_key': license_key
        }
        
        if email:
            payload['increment_uses_count'] = 'true'
        
        try:
            response = requests.post(self.verify_url, data=payload)
            data = response.json()
            
            if data.get('success'):
                purchase = data.get('purchase', {})
                return {
                    'valid': True,
                    'email': purchase.get('email'),
                    'product_name': purchase.get('product_name'),
                    'sale_timestamp': purchase.get('sale_timestamp'),
                    'subscription_active': purchase.get('subscription_cancelled_at') is None,
                    'refunded': purchase.get('refunded', False)
                }
            else:
                return {'valid': False, 'message': data.get('message')}
        
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def activate_license(self, license_key: str, email: str):
        """Activate a license and create user account"""
        verification = self.verify_license(license_key, email)
        
        if not verification.get('valid'):
            return {'success': False, 'error': 'Invalid license key'}
        
        if verification.get('refunded'):
            return {'success': False, 'error': 'This purchase was refunded'}
        
        # Create user account
        conn = sqlite3.connect('apex_production.db')
        cursor = conn.cursor()
        
        try:
            import secrets
            api_key = f"apex_{secrets.token_urlsafe(32)}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO users (email, license_key, api_key, plan, activated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (email, license_key, api_key, 'pro', datetime.now()))
            
            conn.commit()
            
            return {
                'success': True,
                'api_key': api_key,
                'email': email,
                'plan': 'pro'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()

# Usage example
"""
gumroad = GumroadIntegration('apex-swarm-pro')

# User enters license key after Gumroad purchase
result = gumroad.activate_license(
    license_key='XXXX-XXXX-XXXX-XXXX',
    email='user@example.com'
)

if result['success']:
    print(f"Account activated! API Key: {result['api_key']}")
"""
