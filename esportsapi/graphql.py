from . import db_functions as db
import graphene as g

class Team(g.ObjectType):
    id = g.NonNull(g.Int)
    name = g.NonNull(g.String)

class Game(g.ObjectType):
    id = g.NonNull(g.Int)
    name = g.NonNull(g.String)

class Tournament(g.ObjectType):
    id = g.NonNull(g.Int)
    name = g.NonNull(g.String)

class Player(g.ObjectType):
    id = g.NonNull(g.ID)
    name = g.NonNull(g.String)
    birthday = g.Date()
    from_nation = g.String()
    team = g.Field(g.String)
    games = g.NonNull(g.List(g.NonNull(g.String)))

class Match(g.ObjectType):
    id = g.NonNull(g.ID)
    date = g.NonNull(g.DateTime)
    game = g.String()
    finished = g.NonNull(g.Boolean)
    tournament = g.String()
    team1_score = g.Int()
    team2_score = g.Int()
    teams = g.List(g.NonNull(g.List(g.NonNull(Player))))

class MatchInput(g.InputObjectType):
    date = g.NonNull(g.DateTime)
    game_id = g.Int()
    finished = g.Boolean()
    tournament_id = g.Int()
    team1_score = g.Int()
    team2_score = g.Int()
    teams = g.List(g.NonNull(g.List(g.NonNull(g.Int))))

class CreateMatch(g.Mutation):
    class Arguments:
        data = MatchInput(required=True)
    match = g.Field(Match)
    def mutate(root, info, data):
        id = db.insert_match(data)
        d = db.get_matches([id])[id]
        return CreateMatch(match=Match(**d))

class UpdateMatchInput(g.InputObjectType):
    id = g.NonNull(g.Int)
    date = g.DateTime()
    game_id = g.Int()
    finished = g.Boolean()
    tournament_id = g.Int()
    team1_score = g.Int()
    team2_score = g.Int()
    teams = g.List(g.NonNull(g.List(g.NonNull(g.Int))))

class UpdateMatch(g.Mutation):
    class Arguments:
        data = UpdateMatchInput(required=True)
    match = g.Field(Match)
    def mutate(root, info, data):
        db.update_match(data)
        id = data["id"]
        return UpdateMatch(match=Match(**db.get_matches([id])[id]))

class PlayerInput(g.InputObjectType):
    name = g.NonNull(g.String)
    birthday = g.Date()
    from_nation = g.String()
    team_id = g.Int()
    game_ids = g.NonNull(g.List(g.NonNull(g.Int)))

class CreatePlayer(g.Mutation):
    class Arguments:
        data = PlayerInput(required=True)
    player = g.Field(Player)
    def mutate(root, info, data):
        id = db.insert_player(data)
        d = db.get_players([id])[id]
        return CreatePlayer(player=Player(**d))

class CreateTeam(g.Mutation):
    class Arguments:
        name = g.NonNull(g.String)
    team = g.Field(Team)
    def mutate(root, info, name):
        id = db.insert_team(name)
        return CreateTeam(team=Team(**db.get_team(id)))

class CreateGame(g.Mutation):
    class Arguments:
        name = g.NonNull(g.String)
    game = g.Field(Game)
    def mutate(root, info, name):
        id = db.insert_game(name)
        return CreateGame(game=Game(**db.get_game(id)))

class CreateTournament(g.Mutation):
    class Arguments:
        name = g.NonNull(g.String)
    tournament = g.Field(Tournament)
    def mutate(root, info, name):
        id = db.insert_tournament(name)
        return CreateTournament(tournament=Tournament(**db.get_tournament(id)))

# None does not work as default value
_ints = g.List(g.Int, default_value=-1)

class Query(g.ObjectType):
    matches = g.Field(
        g.List(Match),
        between=g.List(g.Date, default_value=-1),
        on_date=g.Date(default_value=-1),
        ids=_ints,
        tournament_name=g.String(default_value=-1),
        tournament_id=g.Int(default_value=-1))
    players = g.Field(
        g.List(Player),
        ids=_ints,
        names=g.List(g.String, default_value=-1))

    def resolve_matches(root, info, between, on_date, ids, tournament_name,
                        tournament_id):
        if ids != -1:
            return db.get_matches(ids).values()
        elif between != -1:
            return db.get_matches_between(*between).values()
        elif on_date != -1:
            return db.get_matches_on_day(on_date).values()
        elif tournament_name != -1:
            return db.get_matches_by_tournament_name(tournament_name).values()
        elif tournament_id != -1:
            return db.get_matches_by_tournament_id(tournament_id).values()

    def resolve_players(root, info, ids, names):
        if ids != -1:
            return db.get_players(ids).values()
        if names != -1:
            return db.get_players_by_names(names).values()

class Mutation(g.ObjectType):
    create_match = CreateMatch.Field()
    create_player = CreatePlayer.Field()
    create_team = CreateTeam.Field()
    create_game = CreateGame.Field()
    create_tournament = CreateTournament.Field()
    update_match = UpdateMatch.Field()
