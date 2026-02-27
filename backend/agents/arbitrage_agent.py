"""
CRYPTO ARBITRAGE AGENT
Finds real arbitrage opportunities across exchanges
NO AI needed - pure math and logic
"""
import ccxt
import asyncio
from typing import List, Dict
import time

class ArbitrageAgent:
    """
    Monitors multiple exchanges for price differences
    Finds profitable arbitrage opportunities
    Works 24/7 without AI
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.exchanges = self._init_exchanges()
        self.opportunities_found = 0
        self.running = True
        
    def _init_exchanges(self):
        """Initialize exchange connections (testnet mode)"""
        exchanges = {}
        
        # Free public APIs - no keys needed for price data
        try:
            exchanges['binance'] = ccxt.binance({'enableRateLimit': True})
        except:
            pass
            
        try:
            exchanges['coinbase'] = ccxt.coinbasepro({'enableRateLimit': True})
        except:
            pass
            
        try:
            exchanges['kraken'] = ccxt.kraken({'enableRateLimit': True})
        except:
            pass
        
        return exchanges
    
    async def get_price(self, exchange_name: str, symbol: str):
        """Get current price from exchange"""
        try:
            exchange = self.exchanges[exchange_name]
            ticker = await exchange.fetch_ticker(symbol)
            return {
                'exchange': exchange_name,
                'symbol': symbol,
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'last': ticker['last']
            }
        except Exception as e:
            return None
    
    async def find_arbitrage(self, symbols: List[str] = ['BTC/USDT', 'ETH/USDT']):
        """Find arbitrage opportunities"""
        opportunities = []
        
        for symbol in symbols:
            prices = {}
            
            # Get prices from all exchanges
            tasks = [self.get_price(ex, symbol) for ex in self.exchanges.keys()]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                if result:
                    prices[result['exchange']] = result
            
            # Find arbitrage
            if len(prices) >= 2:
                exchanges_list = list(prices.keys())
                
                for i in range(len(exchanges_list)):
                    for j in range(i + 1, len(exchanges_list)):
                        buy_ex = exchanges_list[i]
                        sell_ex = exchanges_list[j]
                        
                        buy_price = prices[buy_ex]['ask']
                        sell_price = prices[sell_ex]['bid']
                        
                        if buy_price and sell_price:
                            profit_pct = ((sell_price - buy_price) / buy_price) * 100
                            
                            if profit_pct > 0.5:  # More than 0.5% profit
                                opportunity = {
                                    'symbol': symbol,
                                    'buy_exchange': buy_ex,
                                    'sell_exchange': sell_ex,
                                    'buy_price': buy_price,
                                    'sell_price': sell_price,
                                    'profit_pct': profit_pct,
                                    'timestamp': time.time()
                                }
                                opportunities.append(opportunity)
                                self.opportunities_found += 1
        
        return opportunities
    
    async def run(self):
        """Run agent continuously"""
        print(f"🚀 {self.agent_id} started - Monitoring arbitrage...")
        
        while self.running:
            try:
                opportunities = await self.find_arbitrage()
                
                if opportunities:
                    for opp in opportunities:
                        print(f"💰 ARBITRAGE FOUND!")
                        print(f"   {opp['symbol']}: Buy on {opp['buy_exchange']} @ ${opp['buy_price']:.2f}")
                        print(f"   Sell on {opp['sell_exchange']} @ ${opp['sell_price']:.2f}")
                        print(f"   Profit: {opp['profit_pct']:.2f}%")
                        print()
                
                # Check every 30 seconds
                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(60)
        
        print(f"{self.agent_id} stopped. Found {self.opportunities_found} opportunities.")

# Usage
if __name__ == "__main__":
    agent = ArbitrageAgent("arbitrage-001")
    asyncio.run(agent.run())
