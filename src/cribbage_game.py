from src.scoring import Hand, PeggingPile
from src.player import RandomPlayer, Player
from src.card import Deck
import random


class CribbageGame():
    def __init__(self, player_one=RandomPlayer('AI 1'), player_two=RandomPlayer('AI 2'), winning_score : int=121):
        """
        Initializes the deck, players, crib, pegging pile, dealer and turn counters and target winning score of a cribbage game
        """
        self._deck = Deck()
        self._player_one = player_one
        self._player_two = player_two
        self._crib = Hand()
        self._pegging_pile = PeggingPile()
        self._dealer = random.randint(0, 1)
        self._turn = (self._dealer + 1) % 2
        self._winning_score = winning_score

    def __str__(self) -> str:
        """
        Do note that printing the game as a string gives away player hands, crib and pegging pile
        """
        s = '[Game'
        s += '\n\tPlayer 1: ' + str(self.player_one) + str(self.player_one.hand) + ' score : ' + str(self.player_one.score)
        if self.dealer == self.player_one:
            s += ' <- DEALER'
        s += '\n\tPlayer 2: ' + str(self.player_two) + str(self.player_two.hand) + ' score : ' + str(self.player_two.score)
        if self.dealer == self.player_two:
            s += ' <- DEALER'
        
        s += '\n\tCrib: ' + str(self.crib)
        s += '\n\tPegging Pile: ' + str(self.pegging_pile)
        s += '\n\tDeck: ' + str(self.deck)

        return s + '\n]'

    def __repr__(self) -> str:
        return str(self)

    @property
    def player_one(self) -> Player:
        """
        Return player one
        """
        return self._player_one
    
    @property
    def player_two(self) -> Player:
        """
        Return player two
        """
        return self._player_two

    @property
    def crib(self) -> Hand:
        """
        Returns the Hand representing a crib
        """
        return self._crib

    @property
    def pegging_pile(self) -> PeggingPile:
        """
        Returns the PeggingPile for this game
        """
        return self._pegging_pile

    @property
    def deck(self) -> Deck:
        """
        Returns the deck for this game, with any cards handed out to players not included
        """
        return self._deck

    @property
    def dealer(self) -> Player:
        """
        Returns the current dealer
        """
        if self._dealer == 0:
            return self.player_one
        return self.player_two

    @property
    def non_dealer(self) -> Player:
        """
        Returns whoever is not the dealer
        """
        if self._dealer == 0:
            return self.player_two
        return self.player_one

    @property
    def turn(self) -> Player:
        """
        Returns the player who's turn it currently is
        """
        if self._turn == 0:
            return self.player_one
        return self.player_two

    def _score_hand(self, player : Player):
        """
        Scores points for the given player's hand
        """
        player.score_hand()

    def reset_game(self):
        """
        Reset the game by sending all cards back to the deck, changing the dealer and resetting the turn counter
        """
        self.deck.return_cards_to_deck(self.player_one.clear_hand())
        self.deck.return_cards_to_deck(self.player_two.clear_hand())
        self.deck.return_cards_to_deck(self.crib.cards)
        self.deck.return_cards_to_deck(self.pegging_pile.end_pegging())
        self.crib.discard(self.crib.cards.copy())
        self._turn = self._dealer
        self._dealer = (self._dealer + 1) % 2
        
    def initialize_round(self):
        """
        Initialize a round by shuffling and cutting the deck
        """
        self.deck.shuffle()
        self.deck.cut()

    def start_new_game(self):
        """
        For when you want to fully clear player scores and start a new game
        """
        self.reset_game()
        self._player_one.clear_score()
        self._player_two.clear_score()
        self._dealer = random.randint(0, 1)
        self._turn = (self._dealer + 1) % 2

    def deal_cards(self):
        """
        Deal cards to both players
        """
        self.player_one.get_cards([self.deck.deal_card() for _ in range(6)])
        self.player_two.get_cards([self.deck.deal_card() for _ in range(6)])

    def handle_discards(self):
        """
        Handles discards for the two players, puts their discards into the crib
        """
        if self.dealer == self.player_one:
            dealer = 1
        else:
            dealer = 0
        
        self.crib.add_cards(
            self.player_one.select_discards(dealer=dealer, opp_score=self.player_two.score) 
            + self.player_two.select_discards(dealer=(dealer + 1) % 2, opp_score=self.player_one.score)
        )

    def score_dealer(self, include_top_card=True):
        """
        Scores the dealer hand, including the top card. Can exclude the top card by setting include_top_card to false.
        """
        ### If top card included, add it to the player's hand
        if include_top_card:
            self.dealer.get_cards([self.deck.cards[-1]])

        ### Score the hand, then remove the top card from the player's hand.
        self._score_hand(self.dealer)

        if self.deck.cards[-1] in self.dealer.hand.cards:
            self.dealer.hand.discard([self.deck.cards[-1]])

    def score_crib(self, include_top_card=True):
        """
        Scores the crib and gives those points to the dealer. Can exclude top card by changing it to False.
        """
        if include_top_card:
            self.crib.add_cards([self.deck.cards[-1]])
        
        self.dealer.score_points(self.crib.score)

        if self.deck.cards[-1] in self.crib.cards:
            self.crib.discard([self.deck.cards[-1]])

    def score_non_dealer(self, include_top_card=True):
        """
        Scores the non dealer hand, including the top card. Can exclude the top card by setting include_top_card to false.
        """
        ### If top card included, add it to the player's hand
        if include_top_card:
            self.non_dealer.get_cards([self.deck.cards[-1]])

        ### Score the hand, then remove the top card from the player's hand.
        self._score_hand(self.non_dealer)
        if self.deck.cards[-1] in self.non_dealer.hand.cards:
            self.non_dealer.hand.discard([self.deck.cards[-1]])

    def get_winner(self) -> Player:
        """
        If a player has more than the winning score, return them, starts with player one.
        Note this doesn't take into consideration whether the players both have a winning score and hence this must be used proactively
        """
        if self.player_one.score >= self._winning_score:
            return self.player_one
        if self.player_two.score >= self._winning_score:
            return self.player_two
        
        return None