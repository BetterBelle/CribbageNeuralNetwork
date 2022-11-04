# Cribbage Neural Network

A cribbage game implementation including a deep-q learning implementation aimed at learning how to play cribbage at an optimal level.

# Players

Players hold information about their hand state, name (if given) and have methods to interact with their hand, such as discarding and selecting the card to play during the pegging phase of the game.

# Cards

This file holds information about suits, faces, cards, the deck as well as the pegging pile and a card hand.

## Suits and Faces

These are enum types that hold information about suits and faces such as type, name and values.

## Cards

Card class is simply an implementation holding information about a card's suit and face. 

## Deck

A deck holds all cards and has methods to shuffle, cut the deck as well as dealing out cards or adding them back into the deck.

## Pegging Pile

This holds cards that are part of the current pegging pile, including things like scoring, who's cards belong to who, adding and removing cards from the pile.

## Hand

This is a class embodying a cribbage hand, this includes things like adding and removing cards from the hand (for things like discarding and playing cards into the pegging pile), as well as scoring the hand. This is also used for the crib.

## Cribbage Game

This class handles inputs and outputs to the game and handles turn rotations. It contains all of the players, hands, pegging pile and deck.

It has parameters to manage whether the neural network should be training or playing/testing. 