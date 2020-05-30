from itertools import combinations

from trueskill import Rating, TrueSkill


class TrueSkillMatchmaker:
    class Player:
        def __init__(self, player_id: int, player_name: str, rating: Rating):
            self.player_id: int = player_id
            self.name: str = player_name
            self.rating: Rating = rating
            self.pure_rating: float = 0.0

    class Matchup:
        def __init__(self, team1_ids: list, team2_ids: list, quality: float):
            self.team1_ids = team1_ids
            self.team2_ids = team2_ids
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

        team_1_options = [player_id for i in range(1, len(player_ids) - 1) for player_id in combinations(player_ids, i)]
        for team_1 in team_1_options:
            team_2 = [player_id for player_id in player_ids if player_id not in team_1]
            if team_2 in team_1_options:
                continue
            quality = self.ts.quality([[self.players[player_id].rating for player_id in team_1],
                                       [self.players[player_id].rating for player_id in team_2]])
            result.append(TrueSkillMatchmaker.Matchup(team_1, team_2, quality))

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
