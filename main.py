from src.cribbage_game import CribbageGame
import src.player as player
import multiprocessing
import os
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
    for i in range(20):
        process = multiprocessing.Process(target=run_training_batch, args=[i])
        process.start()
        process.join()
        process.kill()



def run_training_batch(i):
    player_one = player.NetworkPlayer('Network Player')
    game = CribbageGame(player_one)
    if os.path.exists(f'test_network{i-1}.h5'):
        player_one.load_discard_model(f'test_network{i-1}.h5')

    for _ in tqdm(range(50_000)):
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

    # player_one.write_io_to_files()
    player_one.train_discard_model(i)
    f = open('inputs.csv', 'w').close()
    f = open('outputs.csv', 'w').close()
    return



def network_vs_random():
    player_one = player.RandomPlayer('Random Player')
    player_two = player.NetworkPlayer('Network Player')
    player_two.load_discard_model(f'test_network19.h5')
    player_one_wins = 0
    player_two_wins = 0
    game = CribbageGame(player_one, player_two)

    for i in tqdm(range(1_000)):
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



if __name__ == '__main__':
    # random_vs_naive()
    train_discards_solo()
    # network_vs_random()