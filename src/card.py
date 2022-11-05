from enum import Enum
import random

class Suit(Enum):
    DIAMOND = {'value': 0, 'symbol': '♦', 'str': ' of Diamonds'}
    SPADE = {'value': 1, 'symbol': '♠', 'str': ' of Spades'}
    CLUB = {'value': 2, 'symbol': '♣', 'str': ' of Clubs'}
    HEART = {'value': 3, 'symbol': '♥', 'str': ' of Hearts'}

class Face(Enum):
    ACE = {'value': 1, 'symbol': 'A', 'str': 'Ace', 'rank': 1}
    DEUCE = {'value': 2, 'symbol': '2', 'str': 'Deuce', 'rank': 2}
    THREE = {'value': 3, 'symbol': '3', 'str': 'Three', 'rank': 3}
    FOUR = {'value': 4, 'symbol': '4', 'str': 'Four', 'rank': 4}
    FIVE = {'value': 5, 'symbol': '5', 'str': 'Five', 'rank': 5}
    SIX = {'value': 6, 'symbol': '6', 'str': 'Six', 'rank': 6}
    SEVEN = {'value': 7, 'symbol': '7', 'str': 'Seven', 'rank': 7}
    EIGHT = {'value': 8, 'symbol': '8', 'str': 'Eight', 'rank': 8}
    NINE = {'value': 9, 'symbol': '9', 'str': 'Nine', 'rank': 9}
    TEN = {'value': 10, 'symbol': '10', 'str': 'Ten', 'rank': 10}
    JACK = {'value': 10, 'symbol': 'J', 'str': 'Jack', 'rank': 11}
    QUEEN = {'value': 10, 'symbol': 'Q', 'str': 'Queen', 'rank': 12}
    KING = {'value': 10, 'symbol': 'K', 'str': 'King', 'rank': 13}



class Card():
    def __init__(self, face : Face, suit : Suit):
        self._face = face
        self._suit = suit
    
    def __str__(self) -> str:
        return str(self.face.value['symbol']) + str(self.suit.value['symbol'])

    def __repr__(self) -> str:
        return str(self)

    def __lt__(self, other) -> bool:
        if type(other) == Card:
            if self.value == other.value:
                return self.suit.value['value'] < other.suit.value['value']
            return self.value < other.value
        elif type(other) == int:
            return self.value < other
        else:
            raise NotImplementedError()

    def __gt__(self, other) -> bool:
        if type(other) == Card:
            if self.value == other.value:
                return self.suit.value['value'] > other.suit.value['value']
            return self.value > other.value
        elif type(other) == int:
            return self.value > other
        else:
            raise NotImplementedError()

    def __eq__(self, other) -> bool:
        if type(other) == Card:
            return self.face == other.face
        elif type(other) == int:
            return self.value == other
        else:
            raise NotImplementedError

    def __add__(self, other) -> int:
        if type(other) == Card:
            return self.value + other.value
        elif type(other) == int:
            return self.value + other
        else:
            raise NotImplementedError
    
    def __radd__(self, other) -> int:
        if type(other) == Card:
            return self.value + other.value
        elif type(other) == int:
            return self.value + other
        else:
            raise NotImplementedError

    def __sub__(self, other) -> int:
        if type(other) == Card:
            return self.value - other.value
        elif type(other) == int:
            return self.value - other
        else:
            raise NotImplementedError

    def __rsub__(self, other) -> int:
        if type(other) == Card:
            return self.value - other.value
        elif type(other) == int:
            return self.value - other
        else:
            raise NotImplementedError

    @property
    def face(self) -> Face:
        """
        Returns the face of the card
        """
        return self._face

    @property
    def suit(self) -> Suit:
        """
        Returns the suit of the card
        """
        return self._suit

    @property
    def value(self) -> int:
        """
        Get the card's value in cribbage
        """
        return self.face.value['value']



class Deck():
    def __init__(self):
        self._cards = []
        for suit in Suit:
            for face in Face:
                self.cards.append(Card(face, suit))

    def __str__(self) -> str:
        s = '[Deck: '
        for card in self.cards:
            s += (str(card) + ' ')
        return s + ']'

    def __len__(self) -> int:
        return len(self.cards)
        
    @property
    def cards(self) -> list[Card]:
        """
        Return the list of cards in the deck
        """
        return self._cards

    def shuffle(self):
        """
        Shuffles the cards
        """
        random.shuffle(self.cards)

    def cut(self):
        """
        Cut the deck in half, put the bottom of the deck on top
        """
        cut_point = random.randrange(len(self))
        bottom = self.cards[:cut_point]
        top = self.cards[cut_point:]
        self._cards = top + bottom

    def deal_card(self) -> Card:
        """
        Deals the top card of the deck (last element in list). Removes it from the deck and returns it.
        """
        return self.cards.pop()

    def return_cards_to_deck(self, cards : list[Card]):
        """
        Given a list of cards, adds those cards to the deck
        """
        self.cards.extend(cards)