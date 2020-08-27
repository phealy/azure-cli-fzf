# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core import AzCommandsLoader

from azext_fzf_subscription._help import helps  # pylint: disable=unused-import


class Fzf_subscriptionCommandsLoader(AzCommandsLoader):

    def __init__(self, cli_ctx=None):
        from azure.cli.core.commands import CliCommandType
        from azext_fzf_subscription._client_factory import cf_fzf_subscription
        fzf_subscription_custom = CliCommandType(
            operations_tmpl='azext_fzf_subscription.custom#{}',
            client_factory=cf_fzf_subscription)
        super(Fzf_subscriptionCommandsLoader, self).__init__(cli_ctx=cli_ctx,
                                                  custom_command_type=fzf_subscription_custom)

    def load_command_table(self, args):
        from azext_fzf_subscription.commands import load_command_table
        load_command_table(self, args)
        return self.command_table

    def load_arguments(self, command):
        pass


COMMAND_LOADER_CLS = Fzf_subscriptionCommandsLoader
