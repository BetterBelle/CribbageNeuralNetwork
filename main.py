from src.cribbage_game import CribbageGame
import src.player as player
import pickle
import multiprocessing
from tqdm import tqdm


def create_training_batch(num_hands : int = 1_000):
    """
    Creates num_hands hand states and saves them in a file for batch training using experience replay
    """
    player_one = player.RandomPlayer('Naive Player')
    game = CribbageGame(player_one)
    hands = list()

    for _ in tqdm(range(num_hands)):

        ### Initialize, deal and handle discards
        game.initialize_round()
        game.deal_cards()
        hands.append(player_one.hand.cards.copy())

        game.reset_game()

    with open('inputs.txt', 'wb') as f:
        pickle.dump(hands, f)



def train(inputs, i):
    trainee = player.NetworkPlayer('Trainee')
    trainee.train_discard_model(inputs, i)

def train_discards_solo(num_batches : int = 1_000):
    with open('inputs.txt', 'rb') as f:
        inputs = pickle.load(f)
    
    for i in tqdm(range(num_batches)):
        process = multiprocessing.Process(target=train, args=[inputs, i])
        process.start()
        process.join()
        process.kill()


def vs_tester(player_one_type : str = 'random', player_two_type : str = 'random'):
    if player_one_type == 'random':
        player_one = player.RandomPlayer('Random Player 1')
    elif player_one_type == 'network':
        player_one = player.NetworkPlayer('Network Player 1')
        player_one.load_discard_model(f'test_network_best_full.h5')
    elif player_one_type == 'naive':
        player_one = player.NaivePlayer('Naive Player 1')
    elif player_one_type == 'human':
        player_one = player.HumanPlayer('Human Player 1')

    if player_two_type == 'random':
        player_two = player.RandomPlayer('Random Player 2')
    elif player_two_type == 'network':
        player_two = player.NetworkPlayer('Network Player 2')
    elif player_two_type == 'naive':
        player_two = player.NaivePlayer('Naive Player 2')
    elif player_two_type == 'human':
        player_two = player.HumanPlayer('Human Player 2')

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
    player_one.load_discard_model(f'network18.h5')
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
    # vs_tester('network', 'naive')
    # network_init_test()
    create_training_batch()
    train_discards_solo()