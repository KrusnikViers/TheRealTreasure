from itertools import combinations
from math import sqrt

from trueskill import Rating, TrueSkill


class TrueSkillMatchmaker:
    class Player:
        def __init__(self, player_id: int, player_name: str, rating: Rating):
            self.player_id: int = player_id
            self.name: str = player_name
            self.rating: Rating = rating
            self.pure_rating: float = 0.0

    def win_probability(self, team1_ids, team2_ids):
        delta_mu = sum(self.players[player_id].rating.mu for player_id in team1_ids) - \
                   sum(self.players[player_id].rating.mu for player_id in team2_ids)
        sum_sigma = sum(self.players[player_id].rating.sigma ** 2 for player_id in (team1_ids + team2_ids))
        denom = sqrt((len(team1_ids) + len(team2_ids)) * (self.ts.beta * self.ts.beta) + sum_sigma)
        return self.ts.cdf(delta_mu / denom)

    class Matchup:
        def __init__(self, tsmm, team1_ids: list, team2_ids: list, quality: float):
            self.team1_ids = team1_ids
            self.team1_win_chance = tsmm.win_probability(team1_ids, team2_ids)
            self.team2_ids = team2_ids
            self.team2_win_chance = tsmm.win_probability(team2_ids, team1_ids)
            self.quality = quality

    def __init__(self, true_skill: TrueSkill):
        self.ts = true_skill
        self.players = dict()

    def add_player(self, player_id: int, player_name: str, mu: float = None, sigma: float = None):
        if mu is None:
            mu = self.ts.mu
        if sigma is None:
            sigma = self.ts.sigma
        self.players[player_id] = TrueSkillMatchmaker.Player(player_id, player_name, Rating(mu=mu, sigma=sigma))



    def matchups(self, player_ids: list) -> list:
        result = []
        if len(player_ids) < 2:
            return result

        team_1_options = [list(player_id) for i in range(1, len(player_ids)) for player_id in
                          combinations(player_ids, i)]
        calculated_options = []
        for team_1 in team_1_options:
            team_2 = [player_id for player_id in player_ids if player_id not in team_1]
            if team_1 in calculated_options:
                continue
            calculated_options.append(team_2)
            quality = self.ts.quality([[self.players[player_id].rating for player_id in team_1],
                                       [self.players[player_id].rating for player_id in team_2]])
            result.append(TrueSkillMatchmaker.Matchup(self, team_1, team_2, quality))

        return sorted(result, key=lambda x: x.quality, reverse=True)

    def update(self, team_won: list, team_lost: list):
        updated_won, updated_lost = self.ts.rate([[self.players[player_id].rating for player_id in team_won],
                                                  [self.players[player_id].rating for player_id in team_lost]])
        for i in range(0, len(team_won)):
            self.players[team_won[i]].rating = updated_won[i]
        for i in range(0, len(team_lost)):
            self.players[team_lost[i]].rating = updated_lost[i]

        for player_id, player_stats in self.players.items():
            if player_id not in team_won and player_id not in team_lost:
                sigma_diff = self.ts.sigma - player_stats.rating.sigma
                if sigma_diff > 0:
                    old_rating = player_stats.rating
                    player_stats.rating = Rating(old_rating.mu, old_rating.sigma + sigma_diff * 0.05)

    def players_list(self) -> list:
        for player in self.players.values():
            player.pure_rating = self.ts.expose(player.rating)
        return sorted(self.players.values(), key=lambda x: x.pure_rating, reverse=True)
