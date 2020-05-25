import itertools
import math

from trueskill import MU, SIGMA, BETA, Rating, TrueSkill

from app.handlers.context import Context
from app.models.all import Player


def default_ts():
    return TrueSkill(draw_probability=0.0)


def win_probability(team1, team2):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (BETA * BETA) + sum_sigma)
    ts = default_ts()
    return ts.cdf(delta_mu / denom)


def add_player(context: Context):
    player_name = context.command_arguments()
    if not player_name:
        return

    player = context.session.query(Player).filter(Player.name == player_name).first()
    if player:
        context.send_response_message('exists')
        return

    player = Player(name=player_name, mu=MU, sigma=SIGMA)
    context.session.add(player)
    context.send_response_message('created {}'.format(player.name))


def drop_player(context: Context):
    player_name = context.command_arguments()
    if not player_name:
        return

    player = context.session.query(Player).filter(Player.name == player_name).first()
    if not player:
        return

    context.session.delete(player)
    context.send_response_message('deleted {}'.format(player_name))


def list_players(context: Context):
    players = context.session.query(Player).all()
    players.sort(key=lambda p: p.mu, reverse=True)
    for player in players:
        context.send_response_message(
            'player {}: score {}, deviation {}'.format(player.name, round(player.mu, 2), round(player.sigma, 2)))


def add_game(context: Context):
    args = context.command_arguments().split()
    if len(args) < 2:
        return

    winner_team_size = int(args[0])
    winners = [context.session.query(Player).filter(Player.name == name).first() for name in
               args[1:1 + winner_team_size]]
    losers = [context.session.query(Player).filter(Player.name == name).first() for name in args[1 + winner_team_size:]]

    for player in winners + losers:
        if not player:
            context.send_response_message('player not found')
            return

    winners_ratings = [Rating(mu=player.mu, sigma=player.sigma) for player in winners]
    losers_ratings = [Rating(mu=player.mu, sigma=player.sigma) for player in losers]

    new_winners_ratings, new_losers_ratings = default_ts().rate([winners_ratings, losers_ratings])
    for i in range(0, len(new_winners_ratings)):
        winners[i].mu = new_winners_ratings[i].mu
        winners[i].sigma = new_winners_ratings[i].sigma
    for i in range(0, len(new_losers_ratings)):
        losers[i].mu = new_losers_ratings[i].mu
        losers[i].sigma = new_losers_ratings[i].sigma

    list_players(context)


def matchup(context: Context):
    args = context.command_arguments().split()
    if len(args) < 2:
        return

    players = [context.session.query(Player).filter(Player.name == name).first() for name in args]
    for player in players:
        if not player:
            context.send_response_message('player not found')
            return

    ratings = [Rating(mu=player.mu, sigma=player.sigma) for player in players]

    def all_matchups(players_left):
        if players_left:
            current = players_left[0]
            options = all_matchups(players_left[1:])
            result = []
            for option in options:
                result.append((option[0], option[1] + [current]))
                result.append((option[0] + [current], option[1]))
            return result
        return [([], [])]

    matchups = all_matchups(range(0, len(players)))

    qualities = []
    ts = default_ts()
    for setup in matchups:
        if setup[0] and setup[1]:
            qualities.append((ts.quality([[ratings[i] for i in setup[0]], [ratings[i] for i in setup[1]]]), setup))
    qualities.sort(reverse=True)
    for qual in qualities[:20:2]:
        team_1 = [players[i].name for i in qual[1][0]]
        team_2 = [players[i].name for i in qual[1][1]]
        context.send_response_message('{} vs {} : {}'.format(', '.join(team_1), ', '.join(team_2), round(qual[0], 3)))
