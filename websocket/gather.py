import numpy as np

debug = False

'''
This class allows players to gather materials for a fortress which pays the player for their gathered materials.
The player can spend this money in the market. (See market class)
'''


class Gather:
    def __init__(self):
        self.values = {
            "rock": 1,
            "iron": 2,
            "aluminum": 3,
            "copper": 4,
            "lead": 5,
            "zinc": 6,
            "silver": 10,
            "gold": 20,
            "titanium": 100,
            "uranium": 300,
        }
        self.probabilities = {
            "rock": 1 / self.values["rock"],
            "iron": 1 / self.values["iron"],
            "aluminum": 1 / self.values["aluminum"],
            "copper": 1 / self.values["copper"],
            "lead": 1 / self.values["lead"],
            "zinc": 1 / self.values["zinc"],
            "silver": 1 / self.values["silver"],
            "gold": 1 / self.values["gold"],
            "titanium": 1 / self.values["titanium"],
            "uranium": 1 / self.values["uranium"],
        }

    '''selects a mined mineral and returns it'''

    def gather_random(self):
        arr = np.array([*self.probabilities.keys()])
        probs = np.array([*self.probabilities.values()]) / \
            sum([*self.probabilities.values()])
        mined_mat = np.random.choice(arr, 1, replace=True, p=probs)
        if(debug):
            print(*zip(probs, arr))
        print("player mined {}".format(mined_mat))
        return(mined_mat)

    '''returns the summed value of the items'''

    def get_sell_value(self, items_list):
        value = sum([self.values[item] for item in items_list])
        if(debug):
            print("sold {} for {}".format(items_list, value))
        return (value)


# quick and dirty testing
# python gather.py
if __name__ == '__main__':
    g = Gather()
    debug = True
    print(g.gather_random())
    print(g.gather_random())
    print(g.gather_random())
    print(g.gather_random())
    print(g.get_sell_value())
