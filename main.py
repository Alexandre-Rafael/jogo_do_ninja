from src.entities.game import Game


class GameRunner:
    def __init__(self):
        self.game = Game()

    def run(self):
        self.game.run()


if __name__ == '__main__':
    runner = GameRunner()
    runner.run()
