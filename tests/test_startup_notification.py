import ast
import asyncio
import copy
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "mastermelon" / "melon.py"


def parsed_class():
    tree = ast.parse(SOURCE.read_text())
    return next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "bb")


def extracted_async_method(name):
    method = next(
        node
        for node in parsed_class().body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name
    )
    method = copy.deepcopy(method)
    method.decorator_list = []
    module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    namespace = {}
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace[name]


class StartupNotificationTest(unittest.TestCase):
    def test_invite_without_inviter_is_ignored(self):
        class FakeBot:
            inviter_dict = {1: {}}

        class FakeGuild:
            id = 1

        class FakeInvite:
            inviter = None
            uses = 0
            code = "deleted-owner-invite"

        method = extracted_async_method("update_self_invite_dict")
        asyncio.run(method(FakeBot(), FakeGuild(), FakeInvite()))
        self.assertEqual(FakeBot.inviter_dict, {1: {}})

    def test_startup_message_is_sent_before_invite_processing(self):
        on_ready = next(
            node
            for node in parsed_class().body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "on_ready"
        )
        startup_send_line = next(
            node.lineno
            for node in ast.walk(on_ready)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and "melon bot started at" in node.value
        )
        invite_processing_line = next(
            node.lineno
            for node in ast.walk(on_ready)
            if isinstance(node, ast.Attribute) and node.attr == "update_self_invite_dict"
        )
        self.assertLess(startup_send_line, invite_processing_line)


if __name__ == "__main__":
    unittest.main()
