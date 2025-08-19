% Declare predicates that will be modified dynamically
:- dynamic male/1.
:- dynamic female/1.
:- dynamic parent/2.
:- dynamic uncle/2.
:- dynamic aunt/2.

% Gender-based roles
father(X, Y) :- male(X), parent(X, Y).
mother(X, Y) :- female(X), parent(X, Y).

% Child relationships
child(Y, X) :- parent(X, Y).
son(Y, X) :- male(Y), parent(X, Y).
daughter(Y, X) :- female(Y), parent(X, Y).


% Grandparent relationships
grandparent(X, Y) :- parent(X, Z), parent(Z, Y).
grandfather(X, Y) :- male(X), grandparent(X, Y).
grandmother(X, Y) :- female(X), grandparent(X, Y).

% Sibling logic (share at least one parent, and not the same person)
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.
brother(X, Y) :- male(X), sibling(X, Y).
sister(X, Y) :- female(X), sibling(X, Y).

% Uncle and Aunt logic
uncle(X, Y) :- male(X), sibling(X, Z), parent(Z, Y).
aunt(X, Y) :- female(X), sibling(X, Z), parent(Z, Y).

% Relatives (defined loosely here as sibling, parent, or grandparent connection)
relative(X, Y) :- sibling(X, Y).
relative(X, Y) :- parent(X, Y).
relative(X, Y) :- parent(Y, X).
relative(X, Y) :- grandparent(X, Y).
relative(X, Y) :- grandparent(Y, X).
relative(X, Y) :- uncle(X, Y).
relative(X, Y) :- aunt(X, Y).
relative(X, Y) :- uncle(Y, X).
relative(X, Y) :- aunt(Y, X).

% Spouses: they share a child
relative(X, Y) :- parent(X, C), parent(Y, C), X \= Y.

ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).

descendant(Y, X) :- ancestor(X, Y).
