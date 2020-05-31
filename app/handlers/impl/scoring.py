from trueskill import TrueSkill

from app.handlers.context import Context
from app.handlers.impl.trueskill import TrueSkillMatchmaker
from app.models.all import Player

_true_skill = TrueSkill(draw_probability=0.0)


def add_player(context: Context):
    player_name = context.command_arguments()
    if not player_name:
        return

    player = context.session.query(Player).filter(Player.name == player_name).first()
    if player:
        context.send_response_message('exists')
        return

    player = Player(name=player_name, mu=_true_skill.mu, sigma=_true_skill.sigma)
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


def _create_tsmm(context: Context):
    tsmm = TrueSkillMatchmaker(_true_skill)
    players = context.session.query(Player).all()
    for player in players:
        tsmm.add_player(player.id, player.name, player.mu, player.sigma)
    return tsmm


def list_players(context: Context):
    players_list = _create_tsmm(context).players_list()
    desc_list = []
    for player in players_list:
        desc_list.append('{}: {} ({}:{})'.format(player.name, round(player.pure_rating, 1),
                                                 round(player.rating.mu, 2), round(player.rating.sigma, 2)))
    context.send_response_message('\n'.join(desc_list))


def add_game(context: Context):
    args = context.command_arguments().split()
    if len(args) < 2:
        return

    tsmm = _create_tsmm(context)
    winner_team_size = int(args[0])
    winners = [context.session.query(Player).filter(Player.name == name).first().id for name in
               args[1:1 + winner_team_size]]
    losers = [context.session.query(Player).filter(Player.name == name).first().id for name in
              args[1 + winner_team_size:]]
    tsmm.update(winners, losers)

    all_players = context.session.query(Player).all()
    for player in all_players:
        player.mu = tsmm.players[player.id].rating.mu
        player.sigma = tsmm.players[player.id].rating.sigma

    list_players(context)


def matchup(context: Context):
    args = context.command_arguments().split()
    if len(args) < 2:
        return

    players = [context.session.query(Player).filter(Player.name == name).first().id for name in args]
    ttsm = _create_tsmm(context)
    matchups = ttsm.matchups(players)

    def names_list(ttsm: TrueSkillMatchmaker, ids):
        return ', '.join([ttsm.players[player_id].name for player_id in ids])

    def quality_name(quality: float):
        if quality >= 0.52:
            return 'Fair'
        elif quality >= 0.48:
            return 'Unbalanced'
        else:
            return 'Unfair'

    desc_list = []
    for matchup in matchups[:6]:
        desc_list.append('{} option (score: {})\n{} vs {}\n{}% vs {}%\n'.format(
            quality_name(matchup.quality), round(matchup.quality, 2),
            names_list(ttsm, matchup.team1_ids), names_list(ttsm, matchup.team2_ids),
            round(matchup.team1_win_chance * 100.0, 1), round(matchup.team2_win_chance * 100.0, 1)))
    context.send_response_message('\n'.join(desc_list))
