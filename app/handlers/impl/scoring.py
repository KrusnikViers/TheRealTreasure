from app.handlers.context import Context
from app.models.all import Player
from app.database.util import get_with_update


def on_add_player(context: Context):
    player_name = context.command_arguments()
    if not player_name:
        return
    player = get_with_update(context.session, Player, name=player_name)
    context.send_response_message('created {}'.format(player))
