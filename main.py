from src.cribbage_game import CribbageGame
import src.player as player
from tqdm import tqdm

def random_vs_naive():
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



def train_discards_solo():
    player_one = player.NetworkPlayer('Network Player')
    game = CribbageGame(player_one)

    for i in tqdm(range(1_000_000)):
        ### Make sure the player is not the dealer
        if game.dealer == player_one:
            game.reset_game()
        game.initialize_round()
        game.deal_cards()
        game.handle_discards()
        # ### I'm not actually scoring the hand, I just want to know what the score is
        hand_score = player_one.hand.score
        # ### Append the hand score to the target scores of the player
        player_one.append_target_score(hand_score)
        game.reset_game()

    player_one.train_discard_model()



if __name__ == '__main__':
    # random_vs_naive()
    train_discards_solo()