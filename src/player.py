from abc import ABCMeta, abstractmethod
from scoring import Hand, PeggingPile
from card import Card
import random



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

    def get_cards(self, cards : list):
        """
        Add cards to the hand
        """
        self._hand.add_cards(cards)

    def clear_hand(self):
        """
        Function that clears the hand and returns all the cards that were in hand
        """
        cards_in_hand = self.hand
        self.hand.discard(self.hand)
        return cards_in_hand

    @abstractmethod
    def select_discards(self, dealer : int=0, opp_score : int=0) -> list:
        """
        Select cards to place in the crib.
        """
        pass

    @abstractmethod
    def select_peg_card(self, opp_score : int=0, pegging_pile : PeggingPile=None) -> Card:
        """
        Select card to play into the pegging pile
        """
        pass



class RandomPlayer(Player):
    def select_discards(self, dealer : int=0, opp_score : int=0) -> list:
        cards_to_discard = random.sample(self.hand.cards, 2)
        self._hand.discard(cards_to_discard)
        return cards_to_discard

    def select_peg_card(self, opp_score : int=0, pegging_pile : PeggingPile = None) -> Card:
        card_to_play = random.choice(self.hand.cards)
        self._hand.discard([card_to_play])
        return card_to_play



class HumanPlayer(Player):
    def present_cards_for_selection(self, num_cards : int=1):
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

        self._hand.discard(selected_cards)
        return selected_cards

    def select_discards(self, dealer : int=0, opp_score : int=0) -> list:
        return self.present_cards_for_selection(2)

    def select_peg_card(self, opp_score : int=0, pegging_pile : PeggingPile=None) -> Card:
        return self.present_cards_for_selection(1)

