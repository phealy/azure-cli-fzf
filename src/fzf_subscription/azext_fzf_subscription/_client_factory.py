# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

def cf_fzf_subscription(cli_ctx, *_):

    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azext_fzf_subscription.vendored_sdks import SubscriptionClient
    return get_mgmt_service_client(cli_ctx, SubscriptionClient)
