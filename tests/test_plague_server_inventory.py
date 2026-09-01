import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mastermelon" / "console_commands.py"


def function(tree, name):
    return next(
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    )


def assigned_literal(tree, function_name, variable_name):
    fn = function(tree, function_name)
    for node in ast.walk(fn):
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == variable_name for target in node.targets):
                return ast.literal_eval(node.value)
    raise AssertionError(f"{variable_name} was not assigned in {function_name}")


def returned_literal(tree, function_name):
    fn = function(tree, function_name)
    return_node = next(node for node in ast.walk(fn) if isinstance(node, ast.Return))
    if return_node.value is None:
        raise AssertionError(f"{function_name} returned no value")
    return ast.literal_eval(return_node.value)


def node_names(tree):
    fn = function(tree, "getnodes")
    return_node = next(node for node in ast.walk(fn) if isinstance(node, ast.Return))
    if not isinstance(return_node.value, ast.Call) or not return_node.value.args:
        raise AssertionError("getnodes did not return list(enumerate(...))")
    enumerate_call = return_node.value.args[0]
    if not isinstance(enumerate_call, ast.Call) or not enumerate_call.args:
        raise AssertionError("getnodes did not enumerate a node list")
    return ast.literal_eval(enumerate_call.args[0])


class PlagueServerInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(SOURCE.read_text())

    def test_plague_is_a_complete_server_entry_before_afk(self):
        servers = assigned_literal(self.tree, "getservers", "servers")
        folders = returned_literal(self.tree, "servfolders")
        map_folders = returned_literal(self.tree, "mapfolders")

        self.assertEqual(len(servers), len(folders))
        self.assertEqual(len(servers), len(map_folders))

        plague = ("root@23.95.107.12", "plague", "6567", "RN USA2")
        plague_index = servers.index(plague)
        self.assertEqual(plague_index, len(servers) - 2)
        self.assertEqual(servers[-1][1], "test_eu")
        self.assertEqual(folders[plague_index], "/root/Documents/plague")
        self.assertEqual(map_folders[plague_index], "mindustry_maps/plague/")

    def test_plague_node_and_maps_are_present(self):
        self.assertIn("RN USA2", node_names(self.tree))
        map_dir = ROOT / "mindustry_maps" / "plague"
        self.assertEqual(
            {path.name for path in map_dir.glob("*.msav")},
            {"Bridge of Khazad Dum.msav", "SpaceVirusv1.msav", "simplexv2.msav"},
        )

    def test_console_capture_uses_screen_409_compatible_hardcopy(self):
        source = SOURCE.read_text()
        self.assertNotIn('hardcopy -h "screen_log.log"', source)
        self.assertIn('hardcopy "{capture_path}"', source)


if __name__ == "__main__":
    unittest.main()
