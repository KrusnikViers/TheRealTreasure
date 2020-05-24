from app.handlers.actions import Pending
from app.handlers.context import Context
from app.handlers.impl import basic

_PENDING_ACTION_HANDLERS = {
    Pending.REPORT: basic.on_user_report_received,
}


def dispatch_bare_message(context: Context):
    if context.sender and context.update.message:
        action_string = context.sender.reset_pending_action(None, context.update.effective_chat.id)
        if action_string:
            _PENDING_ACTION_HANDLERS[action_string](context)
