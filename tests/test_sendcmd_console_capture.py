import ast
import asyncio
import copy
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "mastermelon" / "console_commands.py"


def parsed_function(name):
    tree = ast.parse(SOURCE.read_text())
    node = next(
        item
        for item in tree.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
    )
    node = copy.deepcopy(node)
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    return module


def extracted_async_function(name, namespace):
    exec(compile(parsed_function(name), str(SOURCE), "exec"), namespace)
    return namespace[name]


class FakeChannel:
    def __init__(self):
        self.messages = []

    async def send(self, message, **kwargs):
        self.messages.append((message, kwargs))


class FakeContext:
    def __init__(self):
        self.channel = FakeChannel()


class NoDelayAsyncio:
    @staticmethod
    async def sleep(_seconds):
        return None


class SendCommandConsoleCaptureTest(unittest.TestCase):
    def test_direct_command_can_target_final_afk_server(self):
        sent = []
        shown = []

        def send_consolecommand(host, command):
            sent.append((host, command))

        async def showconsole(_ctx, i, host, screen, port):
            shown.append((i, host, screen, port))

        servers = [
            (i, "root@example.invalid", f"server_{i}", str(6000 + i), "test")
            for i in range(7)
        ] + [(7, "root@92.119.127.171", "test_eu", "6889", "RN FRN")]
        function = extracted_async_function(
            "send_command_to_1_server",
            {
                "asyncio": NoDelayAsyncio,
                "send_consolecommand": send_consolecommand,
                "showconsole": showconsole,
            },
        )

        asyncio.run(function(FakeContext(), 7, "status", servers))

        self.assertEqual(
            sent,
            [("root@92.119.127.171", 'screen -S test_eu -p 0 -X stuff "status^M"')],
        )
        self.assertEqual(shown, [(7, "root@92.119.127.171", "test_eu", "6889")])

    def test_console_capture_uses_configured_server_folder(self):
        sent = []
        read = []

        def send_consolecommand(host, command):
            sent.append((host, command))

        def ssh_withcmd(host, command):
            read.append((host, command))
            return b"fresh console", b""

        function = extracted_async_function(
            "showconsole",
            {
                "asyncio": NoDelayAsyncio,
                "send_consolecommand": send_consolecommand,
                "ssh_withcmd": ssh_withcmd,
                "servfolders": lambda: ["unused"] * 7 + ["/root/Documents/test_eu"],
            },
        )

        asyncio.run(
            function(
                FakeContext(),
                7,
                "root@92.119.127.171",
                "test_eu",
                "6889",
            )
        )

        capture = "/root/Documents/test_eu/screen_log.log"
        self.assertEqual(
            sent,
            [("root@92.119.127.171", f'screen -S test_eu -p 0 -X hardcopy "{capture}"')],
        )
        self.assertEqual(read, [("root@92.119.127.171", f'cat "{capture}"')])


if __name__ == "__main__":
    unittest.main()
