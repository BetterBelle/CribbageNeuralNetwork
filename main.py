from src.cribbage_game import CribbageGame
import src.player as player
import src.scoring as scoring
import random
import pickle
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
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


def graph_results():
    top_end = list()
    predicted = list()
    with open('results.txt') as f:
        for line in f:
            t, p = [float(i) for i in line.split(',')]
            top_end.append(t)
            predicted.append(p)

    plt.plot(top_end, label='maximum score avg')
    plt.plot(predicted, label='chosen score avg')
    plt.xlabel('batch')
    plt.ylabel('scores')
    plt.title('Average Hand Scores per Batch During Training')
    plt.legend()
    plt.show()
        

def test_with_training_batch():
    network = player.NetworkPlayer()
    network.load_discard_model('network18.h5')
    random_network = player.NetworkPlayer('baseline')
    adversary = player.NaivePlayer('adversary')
    tester = player.NaivePlayer()

    network_scores = list()
    tester_scores = list()
    baseline = list()

    with open('inputs.txt', 'rb') as f:
        inputs = pickle.load(f)

    randomly_chosen = random.sample(inputs, 10)

    for hand in randomly_chosen:
        network._hand = scoring.Hand(hand.copy())
        tester._hand = scoring.Hand(hand.copy())
        random_network._hand = scoring.Hand(hand.copy())
        adversary._hand = scoring.Hand(random.choice(inputs))

        dealer = random.randrange(0, 2)

        random_discards = random_network.select_discards()
        network_discards = network.select_discards(dealer=dealer)
        tester_discards = tester.select_discards()
        adversary_discards = adversary.select_discards()

        tester_crib = scoring.Hand(adversary_discards + tester_discards)
        network_crib = scoring.Hand(adversary_discards + network_discards)
        random_crib = scoring.Hand(adversary_discards + random_discards)

        if dealer:
            baseline.append(random_network.hand.score + random_crib.score - adversary.hand.score)
            network_scores.append(network.hand.score + network_crib.score - adversary.hand.score)
            tester_scores.append(tester.hand.score + tester_crib.score - adversary.hand.score)
        else:
            baseline.append(random_network.hand.score - random_crib.score - adversary.hand.score)
            network_scores.append(network.hand.score - network_crib.score - adversary.hand.score)
            tester_scores.append(tester.hand.score - tester_crib.score - adversary.hand.score)

    plt.plot(network_scores, label='network hand score')
    plt.plot(tester_scores, label='naive hand score')
    plt.plot(baseline, label='baseline hand score')
    plt.xlabel('hand number')
    plt.ylabel('scores')
    plt.title('Hand Scores Over Training Samples')
    plt.legend()
    plt.show()

    print(sum(network_scores) / len(network_scores))
    print(sum(tester_scores) / len(tester_scores))
    print(sum(baseline) / len(baseline))



if __name__ == '__main__':
    # network_init_test()
    # create_training_batch()
    # train_discards_solo()
    # vs_tester('network', 'naive')
    # graph_results()
    test_with_training_batch()