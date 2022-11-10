from src.cribbage_game import CribbageGame
from src.player import RandomPlayer

if __name__ == '__main__':
    player_one = RandomPlayer('Test 1')
    player_two = RandomPlayer('Test 2')
    game = CribbageGame(player_one, player_two)
    while (game.get_winner() == None):
        print('Before Round Start')
        print(game)

        # Initialize round
        game.initialize_round()
        print('Initialized Game')
        print(game)

        # Deal cards
        game.deal_cards()
        print('Dealt Cards')
        print(game)

        # Get players to select discards
        game.handle_discards()
        print('Handled Discards')
        print(game)

        # Score non-dealer hand
        game.score_non_dealer()
        print('Scored for Non-Dealer')
        print(game)

        # If no winner, score dealer hand
        if game.get_winner() == None:
            game.score_dealer()
            print('Scored for Dealer')
            print(game)

        print('After Round End')
        print(game)

        game.reset_game()
        print('After round reset')
        print(game)

    print('The winner is', game.get_winner().name, '!')