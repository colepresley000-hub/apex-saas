"""
DEFI YIELD FARMING AGENT
Scans DeFi protocols for best yields
NO AI needed - just data collection
"""
import requests
from typing import List, Dict
import time

class DeFiYieldAgent:
    """
    Monitors DeFi protocols for yield opportunities
    Compares APYs across platforms
    Finds best farming opportunities
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.opportunities_found = 0
        self.running = True
        
    def get_aave_yields(self):
        """Get Aave lending yields"""
        try:
            # Aave API
            url = "https://aave-api-v2.aave.com/data/liquidity/v2"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            yields = []
            for reserve in data.get('reserves', [])[:5]:
                yields.append({
                    'protocol': 'Aave',
                    'asset': reserve.get('symbol', 'Unknown'),
                    'apy': float(reserve.get('liquidityRate', 0)) * 100,
                    'type': 'Lending'
                })
            
            return yields
        except:
            return []
    
    def get_compound_yields(self):
        """Get Compound yields"""
        try:
            url = "https://api.compound.finance/api/v2/ctoken"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            yields = []
            for token in data.get('cToken', [])[:5]:
                yields.append({
                    'protocol': 'Compound',
                    'asset': token.get('underlying_symbol', 'Unknown'),
                    'apy': float(token.get('supply_rate', {}).get('value', 0)) * 100,
                    'type': 'Lending'
                })
            
            return yields
        except:
            return []
    
    def find_best_yields(self):
        """Find best yields across all protocols"""
        all_yields = []
        
        print(f"🔍 {self.agent_id}: Scanning DeFi protocols...")
        
        # Get yields from different protocols
        all_yields.extend(self.get_aave_yields())
        all_yields.extend(self.get_compound_yields())
        
        # Sort by APY
        all_yields.sort(key=lambda x: x['apy'], reverse=True)
        
        return all_yields[:10]  # Top 10
    
    def run(self):
        """Run agent continuously"""
        print(f"🚀 {self.agent_id} started - Monitoring DeFi yields...")
        
        while self.running:
            try:
                yields = self.find_best_yields()
                
                if yields:
                    print(f"\n💎 TOP DEFI YIELDS:")
                    print("-" * 70)
                    for i, y in enumerate(yields, 1):
                        print(f"{i}. {y['protocol']} - {y['asset']}: {y['apy']:.2f}% APY ({y['type']})")
                    print("-" * 70)
                    
                    self.opportunities_found += len(yields)
                
                # Check every 5 minutes
                time.sleep(300)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)
        
        print(f"{self.agent_id} stopped. Found {self.opportunities_found} opportunities.")

# Usage
if __name__ == "__main__":
    agent = DeFiYieldAgent("defi-001")
    agent.run()
