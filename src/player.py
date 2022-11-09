from abc import ABCMeta, abstractmethod
from scoring import Hand, PeggingPile
from card import Card
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
        cards_in_hand = self.hand.cards
        self.hand.cards.clear()
        return cards_in_hand

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

    def _present_cards_for_selection(self, num_cards : int=1) -> list[Card]:
        """
        Text representation of the hand for the user to select cards to play/discard
        """
        selected_cards = []
        while len(selected_cards) < num_cards:
            selected_cards = []
            s = ''
            for i, card in enumerate(self.hand.cards):
                s += '(' + str(i + 1) + ') ' + str(card) + '\n'

            print('Here are your cards:\n' + s)
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
        return self._present_cards_for_selection(2)

    def select_peg_card(self, opp_score : int=0, pegging_pile : PeggingPile=None) -> list[Card]:
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
            scoring_hand = Hand(self.hand.cards)
            scoring_hand.discard(combination)
            ### When the new hand's score is higher than the recorded highest score, select these discards
            if highest_score <= scoring_hand.score:
                highest_score = scoring_hand.score
                selected_discards = combination

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
        self._pegging_network = self._create_pegging_network()

    def _create_discard_network(self) -> tf.keras.Model:
        """
        Creates the discard network model, also includes preprocessing layers for easier processing.
        """
        pass

    def _create_pegging_network(self) -> tf.keras.Model:
        pass

    def _convert_hand_to_input(self, dealer : int, opp_score : int) -> tf.Tensor:
        pass

    def _convert_pegging_to_input(self, ) -> tf.Tensor:
        pass

    def select_discards(self, dealer : int=0, opp_score : int=0) -> list[Card]:
        self._discard_network.predict()

        return None

