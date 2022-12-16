from abc import ABCMeta, abstractmethod
from src.scoring import Hand, PeggingPile
from src.card import Card, Deck
import pandas as pd
import tensorflow as tf
import random
import itertools



class Player(metaclass=ABCMeta):
    """Abstract Base Class for a Player"""
    def __init__(self, name='John Doe'):
        self._name = name
        self._hand = Hand()
        self._score = 0

    def __str__(self) -> str:
        return '[Player: ' + self.name + ']'

    @property
    def name(self) -> str:
        return self._name

    @property
    def hand(self) -> Hand:
        return self._hand

    @property
    def score(self) -> int:
        return self._score

    def score_points(self, points : int):
        """
        Increase score by given amount of points
        """
        self._score += points

    def score_hand(self):
        self.score_points(self.hand.score)

    def get_cards(self, cards : list[Card]):
        """
        Add cards to the hand
        """
        self._hand.add_cards(cards)

    def clear_hand(self) -> list[Card]:
        """
        Function that clears the hand and returns all the cards that were in hand
        """
        cards_in_hand = self.hand.cards.copy()
        self.hand.cards.clear()
        return cards_in_hand

    def clear_score(self):
        self._score = 0

    @abstractmethod
    def select_peg_card(self, pegging_pile : PeggingPile, opp_score : int=0) -> Card:
        """
        Select card to play into the pegging pile
        """
        ### If no cards can be played into the pile, return a RuntimeError
        card_can_be_played = False
        for card in self.hand.cards:
            if card.value + pegging_pile.current_total <= 31:
                card_can_be_played = True

        if not card_can_be_played:
            raise RuntimeError("Go. Can't play any cards.")

    @abstractmethod
    def select_discards(self, dealer : int=0, opp_score : int=0) -> list[Card]:
        """
        Select cards to place in the crib.
        """
        pass



class RandomPlayer(Player):
    """
    A completely random player that selects discards and pegging cards at random.
    """
    def __init__(self, name='Random Player'):
        super().__init__(name)

    def select_discards(self, dealer : int=0, opp_score : int=0) -> list[Card]:
        cards_to_discard = random.sample(self.hand.cards, 2)
        self.hand.discard(cards_to_discard)
        return cards_to_discard

    def select_peg_card(self, pegging_pile : PeggingPile, opp_score : int=0) -> Card:
        ### First, make sure we can play a card
        super().select_peg_card(pegging_pile)
        ### Select a random card until you pick a card that can be played
        card_to_play = random.choice(self.hand.cards)
        while card_to_play.value + pegging_pile.current_total > 31:
            card_to_play = random.choice(self.hand.cards)
        
        ### Discard that card from hand and return it
        self.hand.discard([card_to_play])
        return card_to_play



class HumanPlayer(Player):
    """
    Player representing a human player. Also handles asking users for input.
    """
    def __init__(self, name='Human Player'):
        super().__init__(name)

    def _present_cards_for_selection(self, num_cards : int=1, dealer : int=0) -> list[Card]:
        """
        Text representation of the hand for the user to select cards to play/discard
        """
        selected_cards = []
        while len(selected_cards) < num_cards:
            selected_cards = []
            s = ''
            for i, card in enumerate(self.hand.cards):
                s += '(' + str(i + 1) + ') ' + str(card) + '\n'

            if dealer == 1:
                print('Here are your cards, you are the dealer:\n' + s)
            else:
                print('Here are your cards, you are not the dealer:\n' + s)
            selection = input('Select ' + str(num_cards) + ' cards: ')
            card_indexes = [int(s) for s in selection.split(' ') if s.isdigit()]
            for i in card_indexes:
                if i < 1 or i > len(self.hand.cards):
                    print(str(i) + ' is an invalid selection.')
                else:
                    selected_cards.append(self.hand.cards[i-1])

        self.hand.discard(selected_cards)
        return selected_cards

    def select_discards(self, dealer : int=0, opp_score : int=0) -> list[Card]:
        return self._present_cards_for_selection(2, dealer=dealer)

    def select_peg_card(self, pegging_pile : PeggingPile, opp_score : int=0, ) -> list[Card]:
        super().select_peg_card(pegging_pile)
        return self._present_cards_for_selection(1)



class NaivePlayer(Player):
    """
    A naive player that selects the card that will net them the most points in the moment without searching.
    """

    def __init__(self, name='Naive Player'):
        super().__init__(name)
    
    def select_discards(self, dealer : int=0, opp_score : int=0) -> list[Card]:
        highest_score = 0
        selected_discards = []
        ### Create every possible combination of discards
        for combination in list(itertools.combinations(self.hand.cards, 2)):
            ### Create a hand with the current combination discarded
            combination = list(combination)
            scoring_hand = Hand(self.hand.cards.copy())
            scoring_hand.discard(combination)
            ### When the new hand's score is higher than the recorded highest score, select these discards
            if highest_score <= scoring_hand.score:
                highest_score = scoring_hand.score
                selected_discards = combination

        self.hand.discard(selected_discards)

        return selected_discards

    def select_peg_card(self, pegging_pile : PeggingPile, opp_score : int=0) -> Card:
        super().select_peg_card(pegging_pile)
        ### If no pegging pile was passed, raise an error
        if pegging_pile == None:
            raise ValueError("You need to pass a pegging pile for this agent to make a decision!")
        highest_score = 0
        selected_card = None

        ### For every card, create a new pegging pile containing the current cards in play and add the new card
        for card in self.hand.cards:
            temp_pile = PeggingPile(pegging_pile.cards_in_play)
            ### If the new card added sends back an error, it means that card can't be played
            try:
                temp_score = temp_pile.add_to_play(card)
            except ValueError:
                ### Can't play this card, set the temp score to less than 0
                temp_score = -1
            
            ### Check the new score
            if highest_score <= temp_score:
                highest_score = temp_pile.score
                selected_card = card

        return selected_card



class NetworkPlayer(Player):
    def __init__(self, name='Network Player'):
        super().__init__(name)
        self._discard_network = self._create_discard_network()
        self._eps = 0.8
        self._decay = 0.9
        
        self._pegging_network = self._create_pegging_network()
        self._converter = self._create_hand_converter()

        self._chosen_arg = 0
        self._output_arr = None
        self._input_tensor = None

        self._discard_mapping = {
            0: (0, 1),
            1: (0, 2),
            2: (0, 3),
            3: (0, 4),
            4: (0, 5),
            5: (1, 2),
            6: (1, 3),
            7: (1, 4),
            8: (1, 5),
            9: (2, 3),
            10: (2, 4),
            11: (2, 5),
            12: (3, 4),
            13: (3, 5),
            14: (4, 5)
        }

    def _create_discard_network(self) -> tf.keras.Model:
        """
        Creates the discard network model
        """
        inputs = tf.keras.layers.Input((321,))
        dense1 = tf.keras.layers.Dense(56, activation='relu')(inputs)
        dense2 = tf.keras.layers.Dense(56, activation='relu')(dense1)
        dense3 = tf.keras.layers.Dense(25, activation='relu')(dense2)
        dense4 = tf.keras.layers.Dense(20, activation='relu')(dense3)
        outputs = tf.keras.layers.Dense(15, activation='linear')(dense4)

        model = tf.keras.Model(inputs=inputs, outputs=outputs, name='crib_discard_model')
        model.compile(optimizer=tf.keras.optimizers.Adam(), loss=tf.keras.losses.MeanAbsoluteError(), metrics=[tf.keras.losses.MeanSquaredError(), tf.keras.losses.Huber()])
        return model

    def _create_pegging_network(self) -> tf.keras.Model:
        """
        Creates the pegging network model
        """
        pass

    def _create_hand_converter(self) -> tf.keras.layers.StringLookup:
        deck_vocabulary = [str(card) for card in Deck().cards]
        return tf.keras.layers.StringLookup(vocabulary=deck_vocabulary, output_mode='one_hot')

    def _convert_hand_to_input(self, dealer : int, opp_score : int) -> tf.Tensor:
        """
        Converts discard input into a tensor and returns it
        """
        ### Create hand as strings, sorted
        sorted_hand = [str(card) for card in sorted(self.hand.cards)]
        encoded_hand = self._converter(sorted_hand)
        collapsed_hand = tf.concat([card for card in encoded_hand], 0)
        return tf.concat([collapsed_hand, [dealer, self.score / 121.0, opp_score / 121.0]], 0)

    def _convert_pegging_to_input(self, dealer : int, opp_score : int, pegging_pile : PeggingPile) -> tf.Tensor:
        pass

    def load_discard_model(self, filename : str):
        """
        Loads the discard model's weights using the given filename
        """
        self._discard_network.load_weights(filename)

    def select_discards(self, dealer : int=0, opp_score : int=0, training : bool = False) -> list[Card]:
        """
        Uses the discard network to determine what cards to discard
        Also saves the input into the player's discard input history
        """
        ### Convert hand, dealer and opponent score as list into self._discard_inputs, then convert it to tensor for prediction
        hand_as_input = tf.convert_to_tensor([self._convert_hand_to_input(dealer, opp_score)])

        ### Get prediction into discard output property
        discard_output = list(self._discard_network.predict(hand_as_input, verbose=0)[0])
        self._output_arr = discard_output

        
        if random.uniform(0, 1) < self._eps and training:
            discard_chosen_index = random.randint(0, 14)
        else:
            ### Convert prediction to index and set discard chosen index to it
            discard_chosen_index = int(tf.argmax(discard_output))

        ### Choose cards using discard mapping, then remove them from hand and return them
        self._chosen_arg = discard_chosen_index
        cards_to_discard_index = self._discard_mapping[discard_chosen_index]
        selected_discards = [sorted(self.hand.cards)[cards_to_discard_index[0]], sorted(self.hand.cards)[cards_to_discard_index[1]]]
        self.hand.discard(selected_discards)

        return selected_discards

    def select_peg_card(self, pegging_pile: PeggingPile, opp_score: int = 0) -> Card:
        """
        Uses the pegging network to select which card to play into the pegging pile
        """
        super().select_peg_card(pegging_pile, opp_score)

        return None

    def train_discard_model(self, hands: list[list[Card]], i: int):
        """
        Requires you to have played discard phases with the model, but trains the model using it's discard input history,
        target scores and chosen index to construct target vectors.
        """
        ### This is to be used if need to read from files instead of just reading from internal variables
        
        replay = 15
        samples = list()
        model_avgs = list()
        tester_avgs = list()

        self._eps *= self._decay ** i
        randomly_chosen = random.sample(hands, 32)
        for hand in randomly_chosen:
            self._hand = Hand(hand.copy())
            samples.append(self._convert_hand_to_input(0, 0))

        samples = tf.convert_to_tensor(samples)

        for _ in range(replay):
            model_scores = list()
            tester_scores = list()
            outputs = list()
            for hand in randomly_chosen:
                self._hand = Hand(hand.copy())
                test_player = NaivePlayer()
                test_player._hand = Hand(hand.copy())
                adversary = NaivePlayer()
                adversary._hand = Hand(random.choice(hands).copy())

                dealer = random.randrange(0, 2)
                tester_discards = test_player.select_discards(0, 0)
                self_discards = self.select_discards(dealer, 0, True)
                adversary_discards = adversary.select_discards(0, 0)


                tester_crib = Hand(tester_discards + adversary_discards)
                self_crib = Hand(self_discards + adversary_discards)

                if dealer:
                    self._output_arr[self._chosen_arg] = self.hand.score + self_crib.score - adversary.hand.score
                    model_scores.append(self.hand.score + self_crib.score - adversary.hand.score)
                    tester_scores.append(test_player.hand.score + tester_crib.score - adversary.hand.score)
                else:
                    self._output_arr[self._chosen_arg] = self.hand.score - self_crib.score - adversary.hand.score
                    model_scores.append(self.hand.score - self_crib.score - adversary.hand.score)
                    tester_scores.append(test_player.hand.score - tester_crib.score - adversary.hand.score)

                outputs.append(self._output_arr)

            model_avgs.append(sum(model_scores) / len(model_scores))
            tester_avgs.append(sum(tester_scores) / len(tester_scores))

            outputs = tf.convert_to_tensor(outputs)
            self._discard_network.fit(samples, outputs, batch_size=32, epochs=1, verbose=0)
        

        with open('results.txt', 'a') as f:
            f.write(str(sum(tester_avgs) / len(tester_avgs)) + ',' + str(sum(model_avgs) / len(model_avgs)) + '\n')
        self._discard_network.save(f'network{i % 20}.h5')

