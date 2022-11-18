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



def train_discards_solo():
    ### Run 1000 batches of hands, this is done to avoid Python leaking memory
    for i in range(1_000):
        process = multiprocessing.Process(target=run_training_batch, args=[i])
        process.start()
        process.join()
        process.kill()



def run_training_batch(i):
    score_ratios = list()
    score_diff = list()

    ### Run batch of 1024 in batches of 32 hands
    for _ in range(32):
        ### Create network player and game
        player_one = player.NetworkPlayer('Network Player')
        game = CribbageGame(player_one)
        
        ### If there exists a network file, load it because it was the last saved weights
        if os.path.exists(f'test_network{i-1}.h5'):
            player_one.load_discard_model(f'test_network{i-1}.h5')

        for _ in tqdm(range(32)):
            ### Make sure the player is not the dealer
            if game.dealer == player_one:
                game.reset_game()

            ### Initialize, deal and handle discards
            game.initialize_round()
            game.deal_cards()
            tester = player.NaivePlayer('Tester')
            tester.hand.add_cards(player_one.hand.cards.copy())

            game.handle_discards()
            test_score = tester.select_discards()

            ### I'm not actually scoring the hand, I just want to know what the score is
            hand_score = player_one.hand.score
            test_score = tester.hand.score

            if test_score > 0:
                score_ratios.append(hand_score / test_score)
            else:
                score_ratios.append(1)
            score_diff.append(test_score - hand_score)

            game.reset_game()

        player_one.train_discard_model(i)

    print('Score Ratios:', str(score_ratios))
    print('Hand Diffs:', str(score_diff))
    print ('Average Score Ratio: ', str(sum(score_ratios) / len(score_ratios)))
    print('Average Hand Difference: ', str(sum(score_diff) / len(score_diff)))
    return

def run_full_training():
    player_one = player.NetworkPlayer('Network Player 1')
    player_two = player.NetworkPlayer('Network Player 2')
    game = CribbageGame(player_one, player_two)

    # Initialize game
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



def network_vs_random():
    player_one = player.RandomPlayer('Random Player')
    player_two = player.NetworkPlayer('Network Player')
    player_two.load_discard_model(f'test_network1.h5')
    player_one_wins = 0
    player_two_wins = 0
    game = CribbageGame(player_one, player_two)

    for i in tqdm(range(1_000)):
        while (game.get_winner() == None):
            # Initialize round
            game.initialize_round()

            # Deal cards
            game.deal_cards()
            # print (game)

            # Get players to select discards
            game.handle_discards()
            

            # Score non-dealer hand
            game.score_non_dealer()

            # If no winner, score dealer hand (with top card)
            if game.get_winner() == None:
                game.score_dealer()
                game.score_crib()
            # print (game)

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



def network_init_test():
    ### Create network player and game
    player_one = player.NetworkPlayer('Network Player')
    game = CribbageGame(player_one)
    player_one.load_discard_model(f'test_network550.h5')
    score_ratios = list()
    score_diff = list()

    ### Run batch of 1000 hands
    for _ in tqdm(range(1_000)):
        ### Make sure the player is not the dealer
        if game.dealer == player_one:
            game.reset_game()

        ### Initialize, deal and handle discards
        game.initialize_round()
        game.deal_cards()
        tester = player.NaivePlayer('Tester')
        tester.hand.add_cards(player_one.hand.cards.copy())

        game.handle_discards()
        tester.select_discards()

        ### I'm not actually scoring the hand, I just want to know what the score is
        hand_score = player_one.hand.score
        test_score = tester.hand.score

        if test_score > 0:
            score_ratios.append(hand_score / test_score)
        else:
            score_ratios.append(1)
        score_diff.append(test_score - hand_score)
        
        ### Append the hand score to the target scores of the player
        game.reset_game()

    for i, j in list(zip(score_ratios, score_diff)):
        print(f'Score Ratio: {i}\nHand Difference: {j}\n')

    print ('Average Score Ratio: ', str(sum(score_ratios) / len(score_ratios)))
    print('Average Hand Difference: ', str(sum(score_diff) / len(score_diff)))




if __name__ == '__main__':
    # random_vs_naive()
    # train_discards_solo()
    # network_vs_random()
    network_init_test()