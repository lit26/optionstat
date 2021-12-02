import numpy as np
import matplotlib.pyplot as plt

PRICE_RANGE_PCT = 0.1

class Leg:
    """Leg
    Single leg of the option trade
    
    Args:
        strike(float): strike price of the option
        premium(float): premium price of the option
        position(int): position of the option trade, negative if selliing
        option_type(str): Call or Put option
        contract_size(int): (optional) contract_size of each option. Default is 100
    """
    def __init__(self, 
                 strike, 
                 premium, 
                 position, 
                 option_type,
                 contract_size=100):
        self._strike = strike
        self._premium = premium
        self._option_type = option_type
        self._position = position
        self._contract_size = contract_size
    
    def get_profit(self, underlying):
        """get profit
        
        Args:
            underlying(float): the stock price at expiration
        """
        price = 0
        if self._option_type == 'Call':
            price = underlying - self._strike
        elif self._option_type == 'Put':
            price = self._strike - underlying
        profit = (max(price, 0) - self._premium) * \
                    abs(self._position) / self._position
        return profit * abs(self._position) * self._contract_size

    
class Optionstat:
    """Optionstat
    Getting plot and stats of option trading
    
    Args:
        contract_size(int): (optional) contract_size of each option. Default is 100
    """
    def __init__(self, contract_size=100):
        self._option_trades = []
        self._strike_prices = []
        self._contract_size = contract_size
    
    def add_trade(self, strike, premium, position, option_type):
        """add option trade leg
        
        Args:
            strike(float): the strike price of the option trade
            premium(float): the premium of the option trade
            position(int): position of the option trade, negative if selliing
            option_type(str): Call or Put option
        """
        trade = Leg(strike, premium, position, option_type, self._contract_size)
        self._option_trades.append(trade)
        self._strike_prices.append(strike)
    
    def _get_price_range(self):
        """add option trade leg
        
        Returns:
            price_range(tuple): default price range for ploting the P/L chart
        """
        price_range_min = min(self._strike_prices) * (1 - PRICE_RANGE_PCT)
        price_range_max = max(self._strike_prices) * (1 + PRICE_RANGE_PCT)
        return (int(price_range_min), int(price_range_max))
    
    def plot(self, price_range=None, current=None, price_increment=0.5):
        """P/L chart
        
        Args:
            price_range(tuple): the price range of the P/L chart
            current(float): current price of the stock
            price_increment(float): price increment of the P/L chart
        """
        if not price_range:
            price_range = self._get_price_range()
        underlying_prices = np.arange(price_range[0], price_range[1] + price_increment, price_increment)
        profits = np.array([sum([trade.get_profit(underlying) for trade in self._option_trades]) 
                  for underlying in underlying_prices])
        
        fig, ax = plt.subplots()
        ax.plot(underlying_prices, profits, color='k')
        if current:
            plt.axvline(x=current, linestyle='--', color='k')
        ax.fill_between(underlying_prices, 0, 
                        profits, profits > 0, color='#20afa1', 
                        alpha=0.5,interpolate=True)
        ax.fill_between(underlying_prices, 0, 
                        profits, profits < 0, color='#e34f4b', 
                        alpha=0.5,interpolate=True)

        ax.set_ylabel('Profit/Loss')
        ax.set_xlabel('Price')
        ax.set_title('P/L chart')
        plt.show()
        return fig, ax
    
    def stat(self):
        """P/L chart
        
        Args:
            price_range(tuple): the price range of the P/L chart
            current(float): current price of the stock
            price_increment(float): price increment of the P/L chart
        Returns:
            stat(dict): the stat of the option strategy
        """
        self._strike_prices.sort()
        underlying_prices = [0] + self._strike_prices + [self._strike_prices[-1] + 1]
        prices = [sum([trade.get_profit(underlying) for trade in self._option_trades]) 
                  for underlying in underlying_prices]
        
        stat = {'legs': len(self._strike_prices)}
        # calculate max profit
        if prices[-1] > prices[-2]:
            stat['max_profit'] = float('inf')
        else:
            stat['max_profit'] = max(prices)
        
        # calculate max loss
        if prices[-1] < prices[-2]:
            stat['max_loss'] = float('-inf')
        else:
            stat['max_loss'] = min(prices)
        
        # calculate break even
        break_even = []
        for i in range(1, len(prices)):
            if prices[i] == prices[i-1]:
                continue
            if prices[i] / abs(prices[i]) == prices[i-1] / abs(prices[i-1]):
                continue
            
            # calculate gradient and intercept
            gradient = (prices[i] - prices[i-1]) / (underlying_prices[i] -underlying_prices[i-1])
            intercept = prices[i] - gradient * underlying_prices[i]
            
            break_even.append(-intercept / gradient)
        stat['break_even'] = break_even
        return stat