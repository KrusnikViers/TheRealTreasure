from app.core.info import PROJECT_FULL_NAME
from app.handlers.actions import Pending
from app.handlers.context import Context
from app.handlers.util.reports import ReportsSender


def on_help_or_start(context: Context):
    message_template = _('{project}_help_for_group') if context.group else _('{project}_help_for_private')
    context.send_response_message(message_template.format(project=PROJECT_FULL_NAME))


def on_reset_action(context: Context, new_action=None):
    action_string = context.sender.reset_pending_action(new_action, context.update.effective_chat.id)
    if action_string:
        context.send_response_message(_('pending_action_cancelled'))


def on_user_report_request(context: Context):
    on_reset_action(context, new_action=Pending.REPORT)
    context.send_response_message(_('waiting_for_{user}_report').format(user=context.sender.name))


def on_user_report_received(context: Context):
    ReportsSender.forward_user_message(context)
    context.send_response_message(_('{user}_report_sent').format(user=context.sender.name))
