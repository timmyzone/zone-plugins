import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/zone-workflow"
SCRIPT = PLUGIN / "skills/zone-pr/scripts/check_versions.py"
spec = importlib.util.spec_from_file_location("versions", SCRIPT)
versions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(versions)


def data(version="6.2.0", base="release/v6.2.0"):
    return {"base": base, "tickets": [{"key": "P-1", "fixVersions": [version]}]}


class VersionTests(unittest.TestCase):
    def test_promotion_route_numeric_order_and_hotfix(self):
        branches = {"main", "release/v6.9.0", "release/v6.9.1", "release/6.10.0", "feature/x"}
        for source, base in [("release/v6.9.0", "release/v6.9.1"),
                             ("release/v6.9.1", "release/6.10.0"),
                             ("release/6.10.0", "main")]:
            with self.subTest(source=source, base=base):
                self.assertEqual(versions.check_promotion_route(source, base, branches),
                                 {"source": source, "base": base, "merge_method": "merge"})
        for source, base in [("release/v6.9.0", "release/6.10.0"),
                             ("release/v6.9.1", "main"),
                             ("release/6.10.0", "release/v6.9.1"),
                             ("release/v6.9.1", "release/v6.9.1")]:
            with self.subTest(source=source, base=base), self.assertRaises(ValueError):
                versions.check_promotion_route(source, base, branches)

    def test_promotion_route_requires_unambiguous_remote_branches(self):
        branches = {"main", "release/v6.9.1"}
        for source, base in [("release/v6.9.0", "main"), (None, "main"),
                             ("main", "main"), ("release/v6.9.1", None),
                             ("release/v6.9.1", "release/v6.10.0")]:
            with self.subTest(source=source, base=base), self.assertRaises(ValueError):
                versions.check_promotion_route(source, base, branches)
        for extra in ["release/6.9.1", "release/v06.9.1", "release/v6.10", "release/latest"]:
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                versions.check_promotion_route("release/v6.9.1", "main", branches | {extra})
        with self.assertRaises(ValueError):
            versions.check_promotion_route("release/v6.9.1", "main", {"release/v6.9.1"})

    def test_promotion_does_not_recheck_ticket_versions(self):
        branches = {"main", "release/v6.9.1", "release/v6.10.0"}
        payload = {**data("6.9.1", "release/v6.10.0"), "kind": "promotion",
                   "source": "release/v6.9.1", "head": "merge/6.9.1-to-6.10.0"}
        self.assertEqual(versions.check_versions(payload, branches),
                         {"kind": "promotion", "source": "release/v6.9.1",
                          "base": "release/v6.10.0", "merge_method": "merge",
                          "ticket_check": "not_checked"})
        payload["kind"] = "change"
        with self.assertRaises(ValueError):
            versions.check_versions(payload, branches)

    def test_pr_kind_and_promotion_source_required(self):
        branches = {"main", "release/v6.2.0"}
        for payload in [{"base": "main", "kind": "promotion"},
                        *[{**data(), "kind": kind} for kind in [None, "", "Promotion", [], {}]]]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                versions.check_versions(payload, branches)
        self.assertEqual(versions.check_versions({**data(), "kind": "change"}, branches),
                         versions.check_versions(data(), branches))

    def test_ticket_optional_branches(self):
        for head in ["chore", "refactor", "chore/deps", "refactor/service"]:
            with self.subTest(head=head):
                payload = {"base": "release/v6.2.0", "head": head, "tickets": []}
                self.assertEqual(versions.check_versions(payload, {"release/v6.2.0"})["ticket_check"], "skipped")
                with self.assertRaises(ValueError):
                    versions.check_versions(payload, set())
                payload["tickets"] = data("6.3.0")["tickets"]
                with self.assertRaises(ValueError):
                    versions.check_versions(payload, {"release/v6.2.0"})
        for head in ["feature/x", "chorefix", "feature/chore/x", "refactor/", "Chore/x", None]:
            with self.subTest(head=head), self.assertRaises(ValueError):
                versions.check_versions({"base": "main", "head": head, "tickets": []},
                                        {"main", "release/v6.3.0"})

    def test_prefix_policy(self):
        for version in ["6.2.0", " v6.2.0(後端) ", "6.2.0-hotfix", "6.2.00", "6.2.01"]:
            with self.subTest(version=version):
                self.assertEqual(
                    versions.check_versions(data(version), {"release/v6.2.0"})["expected"],
                    "6.2.0",
                )
        for version in ["6.2.1", "6.3.0", "16.2.0", "vv6.2.0", ""]:
            with self.subTest(version=version), self.assertRaises(ValueError):
                versions.check_versions(data(version), {"release/v6.2.0"})

    def test_main_numeric_order_and_target(self):
        branches = {"main", "release/v6.9.9", "release/6.10.1", "release/v6.10.0"}
        self.assertEqual(
            versions.check_versions(data("v6.11.01", "main"), branches)["expected"],
            "6.11.0",
        )
        for version in ["6.10.1", "6.12.0", "7.0.0"]:
            with self.subTest(version=version), self.assertRaises(ValueError):
                versions.check_versions(data(version, "main"), branches)
        with self.assertRaises(ValueError):
            versions.check_versions(data("6.4.0", "main"), {"main"})

    def test_complete_base_required(self):
        self.assertEqual(
            versions.check_versions(data(base="release/6.2.0"), {"release/6.2.0"})["expected"],
            "6.2.0",
        )
        for base in ["6.2.0", "develop", "release/v6.2", "release/v6.2.0"]:
            with self.subTest(base=base), self.assertRaises(ValueError):
                versions.check_versions(data(base=base), {"develop", "release/v6.2"})

    def test_ticket_boundaries(self):
        for tickets in [[], None, [{}], [None],
                        [{"key": "P-1", "fixVersions": []}],
                        [{"key": "P-1", "fixVersions": ["6.2.0", "6.4.0"]}],
                        [{"key": "P-1", "fixVersions": [None]}],
                        data()["tickets"] * 2,
                        data()["tickets"] + [{"key": "P-2", "fixVersions": ["6.3.0"]}]]:
            with self.subTest(tickets=tickets), self.assertRaises(ValueError):
                versions.check_versions({"base": "release/v6.2.0", "tickets": tickets},
                                        {"release/v6.2.0"})
        two = data()
        two["tickets"].append({"key": "P-2", "fixVersions": ["6.2.01"]})
        self.assertEqual(versions.check_versions(two, {"release/v6.2.0"})["tickets"],
                         ["P-1", "P-2"])

    def test_cli_local_remote_and_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory) / "installed plugin"
            shutil.copytree(PLUGIN, installed, ignore=shutil.ignore_patterns("__pycache__"))
            repo = Path(directory) / "target repo"
            repo.mkdir()
            def git(*args):
                return subprocess.run(["git", *args], cwd=repo, check=True,
                                      capture_output=True, text=True)
            git("init", "-b", "main")
            git("-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "--allow-empty", "-m", "fixture")
            git("branch", "release/v6.3.0")
            git("branch", "release/v6.2.0")
            input_file = repo / "input.json"
            input_file.write_text(json.dumps(data("6.4.0", "main")))
            command = [sys.executable, str(installed / SCRIPT.relative_to(PLUGIN)),
                       str(input_file), "--remote", str(repo)]
            result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["expected"], "6.4.0")
            promotion = {**data("6.2.0", "release/v6.3.0"), "kind": "promotion",
                         "source": "release/v6.2.0"}
            input_file.write_text(json.dumps(promotion))
            result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout),
                             {"kind": "promotion", "source": "release/v6.2.0",
                              "base": "release/v6.3.0", "merge_method": "merge",
                              "ticket_check": "not_checked"})
            input_file.write_text(json.dumps({**promotion, "base": "main"}))
            result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("BLOCKED", result.stderr)
            result = subprocess.run(command[:-1] + [str(repo / "missing")],
                                    cwd=repo, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("BLOCKED", result.stderr)
            input_file.write_text("{")
            result = subprocess.run(command, cwd=repo, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)


class PackageTests(unittest.TestCase):
    def test_manifests_and_marketplace_paths(self):
        manifests = [json.loads((PLUGIN / path / "plugin.json").read_text())
                     for path in [".claude-plugin", ".codex-plugin"]]
        self.assertEqual(manifests[0]["name"], manifests[1]["name"])
        self.assertEqual(manifests[0]["version"], manifests[1]["version"])
        self.assertRegex(manifests[0]["version"], r"^[0-9]+\.[0-9]+\.[0-9]+$")
        for manifest in manifests:
            self.assertTrue(manifest["description"])
            self.assertTrue(manifest["author"]["name"])
        self.assertEqual((PLUGIN / manifests[1]["skills"]).resolve(), PLUGIN / "skills")
        for relative in [".claude-plugin/marketplace.json", ".agents/plugins/marketplace.json"]:
            catalog = json.loads((ROOT / relative).read_text())
            entry = catalog["plugins"][0]
            source = entry["source"]
            path = source["path"] if isinstance(source, dict) else source
            self.assertEqual((ROOT / path).resolve(), PLUGIN)
            self.assertEqual(entry["name"], manifests[0]["name"])

    def test_bundled_links_and_no_external_skill_dependency(self):
        for path in PLUGIN.rglob("*.md"):
            text = path.read_text()
            self.assertNotIn("/Users/", text, path)
            self.assertNotIn("~/.agents/skills", text, path)
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if "://" not in target:
                    resolved = (path.parent / target).resolve()
                    self.assertTrue(resolved.is_file(), (path, target))
                    self.assertIn(PLUGIN, resolved.parents)
        for name in ["zone-pr", "zone-review"]:
            text = (PLUGIN / "skills" / name / "SKILL.md").read_text()
            self.assertTrue(text.startswith(f"---\nname: {name}\ndescription: "))


if __name__ == "__main__":
    unittest.main()
