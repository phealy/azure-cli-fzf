# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.commands import CliCommandType
from azext_fzf._client_factory import cf_fzf


def load_command_table(self, _):
    with self.command_group('fzf') as g:
        g.custom_command('install', 'fzf_install', is_preview=True)
        g.custom_command('group', 'fzf_group', is_preview=True)
        g.custom_command('location', 'fzf_location', is_preview=True)
        g.custom_command('subscription', 'fzf_subscription', is_preview=True)


    with self.command_group('fzf', is_preview=True):
        pass

