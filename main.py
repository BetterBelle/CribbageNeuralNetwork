from src.cribbage_game import CribbageGame
from src.player import RandomPlayer, HumanPlayer

if __name__ == '__main__':
    player_one = RandomPlayer('Test 1')
    player_two = HumanPlayer('Test 2')
    game = CribbageGame(player_one, player_two)
    while (game.get_winner() == None):
        # Initialize round
        game.initialize_round()

        # Deal cards
        game.deal_cards()

        # Get players to select discards
        game.handle_discards()

        # Score non-dealer hand
        game.score_non_dealer()

        # If no winner, score dealer hand (with top card)
        if game.get_winner() == None:
            game.score_dealer()
            game.score_crib()

        # Reset game (collect all cards)
        game.reset_game()

    print('The winner is', game.get_winner().name, '!')