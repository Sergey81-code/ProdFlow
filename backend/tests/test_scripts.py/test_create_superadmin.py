from unittest.mock import ANY, AsyncMock, patch
from uuid import uuid4

import pytest


from scripts.create_superadmin import (
    prompt_for_superadmin_credentials,
)


@patch("scripts.create_superadmin.get_password", return_value="StrongPass1!")
@patch("builtins.input", side_effect=["super_admin", "Super", "Admin"])
async def test_prompt_valid(mock_input, mock_getpass):
    with patch(
        "scripts.create_superadmin.create_superadmin", new_callable=AsyncMock
    ) as mock_create:
        await prompt_for_superadmin_credentials()
        mock_create.assert_called_once_with(
            "super_admin", "StrongPass1!", "Super", "Admin", ANY
        )


@patch(
    "scripts.create_superadmin.get_password",
    side_effect=["invalid", "StrongPass1!", "StrongPass1!"],
)
@patch("builtins.input", side_effect=["user1", "Super", "Admin"])
async def test_prompt_invalid_password(mock_input, mock_getpass):
    with patch(
        "scripts.create_superadmin.create_superadmin", new_callable=AsyncMock
    ) as mock_create:
        await prompt_for_superadmin_credentials()
        mock_create.assert_called_once_with(
            "user1", "StrongPass1!", "Super", "Admin", ANY
        )


@patch(
    "scripts.create_superadmin.get_password",
    side_effect=["StrongPass1!", "StrongPass2!", "StrongPass1!"],
)
@patch("builtins.input", side_effect=["user2", "Super", "Admin"])
async def test_prompt_passwords_do_not_match(mock_input, mock_getpass):
    with patch(
        "scripts.create_superadmin.create_superadmin", new_callable=AsyncMock
    ) as mock_create:
        await prompt_for_superadmin_credentials()
        mock_create.assert_called_once_with(
            "user2", "StrongPass1!", "Super", "Admin", ANY
        )


async def test_prompt_exit():
    with patch("builtins.input", side_effect=["exit"]), patch(
        "sys.exit", side_effect=SystemExit(0)
    ) as mock_exit:
        with pytest.raises(SystemExit):
            await prompt_for_superadmin_credentials()
        mock_exit.assert_called_once_with(0)
