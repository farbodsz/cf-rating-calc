"""Classes representing objects from the Codeforces API, and functions for
deserializing them from JSON format.
"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class RatingChange:
    """Represents the participation of a user in a rated contest.

    See: https://codeforces.com/apiHelp/objects#RatingChange
    """

    handle: str
    rank: int
    old_rating: int
    new_rating: int


def deserialize_rating_change(data):
    """Constructs a RatingChange instance from the JSON object.

    Arguments:
      data    a RatingChange in JSON format
    """
    handle = data["handle"]
    rank = data["rank"]
    old_rating = data["oldRating"]
    new_rating = data["newRating"]
    return RatingChange(handle, rank, old_rating, new_rating)


@dataclass(frozen=True)
class Party:
    """Represents a party participating in a contest.

    This object holds a list of handles: a handle per member in the party.

    See: https://codeforces.com/apiHelp/objects#Party
    """

    handles: Tuple[str]


def deserialize_party(data):
    """Constructs a Party instance from the JSON object.

    Arguments:
      data    a Party in JSON format
    """
    members = []
    for row in data["members"]:
        members.append(row["handle"])
    return Party(tuple(members))


@dataclass(frozen=True)
class StandingsRow:
    """Represents a row in a list of standings/ranks.

    See: https://codeforces.com/apiHelp/objects#RanklistRow
    """

    party: Party
    rank: int
    points: int
    penalty: int


def deserialize_standings_row(data):
    """Constructs a StandingsRow instance from the JSON object.

    Arguments:
      data    a StandingsRow in JSON format
    """
    party = deserialize_party(data["party"])
    rank = data["rank"]
    points = data["points"]
    penalty = data["penalty"]
    return StandingsRow(party, rank, points, penalty)
