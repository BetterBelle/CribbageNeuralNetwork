from src.cribbage_game import CribbageGame
import src.player as player
from tqdm import tqdm

if __name__ == '__main__':
    player_one = player.NaivePlayer('Test 1')
    player_two = player.RandomPlayer('Test 2')
    player_one_wins = 0
    player_two_wins = 0
    game = CribbageGame(player_one, player_two)

    for i in tqdm(range(1_000_000)):
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

        if game.get_winner() == player_one:
            player_one_wins += 1
        else:
            player_two_wins += 1
        game.start_new_game()

    print('The final score was: ')
    print(str(player_one) + ': ' + str(player_one_wins))
    print(str(player_two) + ': ' + str(player_two_wins))