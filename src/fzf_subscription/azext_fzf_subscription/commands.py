# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
from azure.cli.core.commands import CliCommandType
from azext_fzf_subscription._client_factory import cf_fzf_subscription


def load_command_table(self, _):

    fzf_subscription_sdk = CliCommandType(client_factory=cf_fzf_subscription)

    with self.command_group('account', fzf_subscription_sdk, client_factory=cf_fzf_subscription) as g:
        g.custom_command('select', 'fzf_account_select', is_preview=True)

