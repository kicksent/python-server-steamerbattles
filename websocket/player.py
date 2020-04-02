playerList = {}


def show_logged_in():
    for player in playerList:
        print("All players:")
        print(playerList[player], playerList[player].name,
              playerList[player].position)


class Entity:
    def __init__(self, name):
        self.name = name
        self.health = 15,
        self.shield = 15,

    def takeDamage(self, damage=10):
        self.shield -= damage
        if self.shield < 0:
            self.health += self.shield
            self.shield = 0
        print("Fortress took {} damage! username: {}".format(damage, self.name))
        self.hasDied()

    def hasDied(self):
        if(self.health < 0):
            self.killSelf()


class Player(Entity):
    def __init__(self, name):
        # inherit all the properties of the parent
        super().__init__(name)
        self.position = [0, 0]

    def setPosition(self, position):
        self.position = position

    def killSelf(self):
        playerList[self.name] = None


class Player(Entity):
    def __init__(self, name):
        # inherit all the properties of the parent
        super().__init__(name)

    def killSelf(self):
        fortList[self.name] = None


def main():
    playerList["testUsername"] = Player("testUsername")
    print(playerList)
    playerList["testUsername"].takeDamage()
    show_logged_in()


class GameEngine:
    def handle_events():
        return

    def update():
        return

    def draw():
        # since drawing happens in the client, this should simply tell the client that a cycle has completed
        return


if __name__ == '__main__':
    main()
