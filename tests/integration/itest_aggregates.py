import pytest
import json
from typing import Dict

from aleph_client.user_session import AuthenticatedUserSession
from tests.integration.toolkit import try_until
from .config import REFERENCE_NODE, TARGET_NODE

from aleph_client.types import Account


async def create_aggregate_on_target(
    account: Account,
    key: str,
    content: Dict,
    emitter_node: str,
    receiver_node: str,
    channel="INTEGRATION_TESTS",
):
    async with AuthenticatedUserSession(
        account=account, api_server=emitter_node
    ) as tx_session:
        aggregate_message, message_status = await tx_session.create_aggregate(
            key=key,
            content=content,
            channel="INTEGRATION_TESTS",
        )

    assert aggregate_message.sender == account.get_address()
    assert aggregate_message.channel == channel
    # Note: lots of duplicates in the response
    item_content = json.loads(aggregate_message.item_content)
    assert item_content["key"] == key
    assert item_content["content"] == content
    assert item_content["address"] == account.get_address()
    assert aggregate_message.content.key == key
    assert aggregate_message.content.address == account.get_address()
    assert aggregate_message.content.content == content

    async with AuthenticatedUserSession(
        account=account, api_server=receiver_node
    ) as rx_session:
        aggregate_from_receiver = await try_until(
            rx_session.fetch_aggregate,
            lambda aggregate: aggregate is not None,
            timeout=5,
            address=account.get_address(),
            key=key,
        )

    for key, value in content.items():
        assert key in aggregate_from_receiver
        assert aggregate_from_receiver[key] == value


@pytest.mark.asyncio
async def test_create_aggregate_on_target(fixture_account):
    """
    Attempts to create an aggregate on the target node and validates that the aggregate can be fetched
    from the reference node.
    """
    await create_aggregate_on_target(
        fixture_account,
        key="test_target",
        content={"a": 1, "b": 2},
        emitter_node=TARGET_NODE,
        receiver_node=REFERENCE_NODE,
    )


@pytest.mark.asyncio
async def test_create_aggregate_on_reference(fixture_account):
    """
    Attempts to create an aggregate on the reference node and validates that the aggregate can be fetched
    from the target node.
    """
    await create_aggregate_on_target(
        fixture_account,
        key="test_reference",
        content={"c": 3, "d": 4},
        emitter_node=REFERENCE_NODE,
        receiver_node=TARGET_NODE,
    )
