# Copyright 2025 GARR.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r"""
Generic CLI client to connect in SSH to a remote host using an xterm window.

Example:
    device = {
        "host": "192.168.0.1",
        "port": 22,
        "username": os.environ["USER"],
        "password": os.environ["PASSWORD"],
    }

    async with AsyncSshTerminal(**device) as session:
        await session.execute_command("")

        output = await session.execute_command("show shelf shelf-id")
        print(output)

        await session.change_user_or_host(
            "shell -f",
            user_at_host_prompt="/home/user$",
        )
"""

from services.asyncsshcli.client import AsyncSshTerminal

async_ssh_cli = AsyncSshTerminal

__all__ = ["async_ssh_cli"]
