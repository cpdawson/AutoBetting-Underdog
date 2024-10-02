class BetStat:
    def __init__(self, player_name, matchup, stat_type, line, over_under, hit_percentage):
        self.player_name = player_name
        self.matchup = matchup
        self.stat_type = stat_type
        self.line = line
        self.over_under = over_under
        self.hit_percentage = hit_percentage

    def __repr__(self):
        return (f"PlayerStat(player_name='{self.player_name}', matchup='{self.matchup}', "
                f"stat_type='{self.stat_type}', line='{self.line}', "
                f"over_under='{self.over_under}', hit_percentage='{self.hit_percentage}')")

