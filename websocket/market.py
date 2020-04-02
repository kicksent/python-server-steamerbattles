
'''
The market is the class that controls user purchases
'''


class Market:
    def __init__(self):
        self.types = {
            "basic": 0,
            "miner": 2000,
            "fighter": 2000,
            "assassin": 2000,
        }
        self.upgrades = {
            "cargo": 2000,
            "plating": 2000,
            "stealth": 5000,
        }

    def get_cost(self, purchase_key):
        if(purchase_key in self.types):
            return(self.types[purchase_key])
        if(purchase_key in self.upgrades):
            return(self.upgrades[purchase_key])
        else:
            return(10000000)
