"""Repo rules: manifests parse, skills are well-formed, always-on files stay lean,
every {{TOKEN}} a skill uses is defined in a profile template.

Lean ratchet: tests/lean_baseline.json holds the measured sizes. Nothing may grow
past it. When a change shrinks something, lock the gain in:
    python3 tests/test_repo.py --write-baseline
(the spec allowlist in that file is never rewritten - shrink it by hand).
"""
import itertools
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "creator-management-inbox")
SKILLS = os.path.join(PLUGIN, "skills")
PROGRAM = os.path.join(PLUGIN, "program")
TEMPLATES = os.path.join(SKILLS, "company-context", "templates")

WORKFLOW = os.path.join(SKILLS, "inbox-auto-draft-workflow")
BASELINE = os.path.join(ROOT, "tests", "lean_baseline.json")
SPEC_SKILL_LINES = 500          # Agent Skills spec: keep SKILL.md under 500 lines
SPEC_DESCRIPTION_CHARS = 1024   # Agent Skills spec: description max length
NGRAM = 12                      # a shared 12-word run = duplicated text
TOKEN = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
LITERAL_OK = {"TOKEN"}

# One rule, one home: each rule is stated in exactly one file, marked
# <!-- rule:ID --> (optionally "overridable"); every other file points to the ID.
RULE = re.compile(r"<!--\s*rule:([a-z0-9-]+)((?:\s+[a-z-]+)*)\s*-->")
OVERRIDE = re.compile(r"<!--\s*override:([a-z0-9-]+)\s*-->")
RULE_FLAGS = {"overridable"}
# Test 8: words that belong to a pack or a module, never to the core every program
# loads. The only per-file exception: creator-notes, whose birthday gifting is core.
CORE_DENY_CI = re.compile(
    r"affiliat|commission|median views|PLAN_(TOP|MID|FREE)|TRIAL_TERMS|CREDIT_UNIT|subscri|"
    r"\bsubs\b|sign-?ups?|two-piece|Track [AB]|TRACK_GATE|SUB_VALUE_YARDSTICK|boost|whitelist|"
    r"seeding|tutorial|YouTube integration|gift", re.I)
CORE_DENY_CS = re.compile(r"\bCPM\b|\bPro\b|\bPO\b|W-[89]")
CORE_ALLOW = {"skills/creator-notes/SKILL.md": {"gift"}}  # birthdays and gifting
ROUTING_PATH = re.compile(r"`((?:inbox-auto-draft-workflow/|negotiation-playbook/)?"
                          r"(?:shapes|references|program)/[\w./-]+)`")

REQUIRED_RULES = {
    "aff-entry", "above-band", "one-move-per-draft", "conversion-bar", "claims-handling",
    "follow-up-ladder", "first-number", "restate-ask", "rights-pricing", "done-claims",
    "limited-authority", "package-pricing", "unseen-content",
}


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def md_files(root):
    for d, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".md"):
                yield os.path.join(d, f)


# --- lean measurements ------------------------------------------------------
def rel(path):
    return os.path.relpath(path, PLUGIN).replace(os.sep, "/")


def skill_names():
    return sorted(n for n in os.listdir(SKILLS)
                  if os.path.exists(os.path.join(SKILLS, n, "SKILL.md")))


def description(name):
    """The frontmatter description, folded to one line as a loader sees it."""
    head = read(os.path.join(SKILLS, name, "SKILL.md")).split("---")[1]
    m = re.search(r"^description:[ \t]*(?:[>|][-+]?)?[ \t]*\n?(.*?)(?=^\S|\Z)", head,
                  re.S | re.M)
    return " ".join(x.strip() for x in m.group(1).strip().splitlines())


def always_on_files():
    """The always-on set, read from the workflow SKILL's own "Always loaded"
    line, so the test measures whatever the workflow actually loads."""
    text = read(os.path.join(WORKFLOW, "SKILL.md"))
    m = re.search(r"\*\*Always loaded.*?(?:\n\s*\n)", text, re.S)
    assert m, "workflow SKILL.md has no 'Always loaded' line"
    profile_only = set(os.listdir(TEMPLATES)) | {"house-rules.md"}
    files = [os.path.join(WORKFLOW, "SKILL.md")]
    for tok in re.findall(r"`([^`]+)`", m.group(0)):
        if os.path.isdir(os.path.join(SKILLS, tok)):
            files.append(os.path.join(SKILLS, tok, "SKILL.md"))
        elif os.path.isfile(os.path.join(WORKFLOW, tok)):
            files.append(os.path.join(WORKFLOW, tok))
        else:
            assert tok in profile_only, f"always-on item `{tok}` is neither a plugin file nor a profile file"
    return files


def dup_text_files():
    """Plugin prose that should never repeat itself. Templates, the demo and the
    fictional example voice are copies by design."""
    return sorted(f for f in md_files(PLUGIN)
                  if not rel(f).startswith("demo/") and "/templates/" not in rel(f)
                  and not f.endswith("example-voice.md"))


def ngrams(path, n=NGRAM):
    words = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", read(path).lower())
    return {" ".join(words[i:i + n]) for i in range(len(words) - n + 1)}


PHRASEBOOK = re.compile(r"^#+\s.*(phrasebook|sent-diff)", re.I | re.M)


def measure():
    m = {"skill_lines": {}, "description_chars": {}, "file_lines": {}}
    for n in skill_names():
        m["skill_lines"][n] = len(read(os.path.join(SKILLS, n, "SKILL.md")).splitlines())
        m["description_chars"][n] = len(description(n))
    m["description_total_chars"] = sum(m["description_chars"].values())
    for f in sorted(list(md_files(SKILLS)) + list(md_files(PROGRAM))):
        m["file_lines"][rel(f)] = len(read(f).splitlines())
    m["file_lines_total"] = sum(m["file_lines"].values())
    ao = {rel(f): {"lines": len(read(f).splitlines()), "words": len(read(f).split())}
          for f in always_on_files()}
    m["always_on"] = {"files": ao, "lines": sum(v["lines"] for v in ao.values()),
                      "words": sum(v["words"] for v in ao.values())}
    grams = {rel(f): ngrams(f) for f in dup_text_files()}
    m["shared_12_word_runs"] = {f"{a} | {b}": len(grams[a] & grams[b])
                                for a, b in itertools.combinations(sorted(grams), 2)
                                if grams[a] & grams[b]}
    m["phrasebook_headings"] = sorted(f"{rel(f)}: {h.group(0).strip()}"
                                      for f in md_files(SKILLS)
                                      for h in PHRASEBOOK.finditer(read(f)))
    return m


def baseline():
    return json.loads(read(BASELINE))


# --- program load plans (tests 5 and 9) ---------------------------------------
sys.path.insert(0, os.path.join(PLUGIN, "scripts"))
from inbox_lib import program as program_lib  # noqa: E402


def manifest():
    return json.loads(read(os.path.join(PROGRAM, "manifest.json")))


def block_sizes(man=None):
    """Worst-case plugin lines per block for the neutral core and each built pack
    with its default modules, plus always-on + the heaviest single routing row
    (a block's base load and its largest on-trigger file)."""
    man = man or manifest()
    configs = {"neutral": (None, [])}
    for name, pack in man["packs"].items():
        if pack["status"] == "built":
            configs[name] = (name, [{"name": m} for m in pack["default_modules"]])
    out = {}
    for cfg, (pack, mods) in configs.items():
        plan, missing = program_lib.load_plan(man, PLUGIN, pack, mods, [])
        assert not missing, f"manifest file missing: {missing}"
        sizes = {b: plan[b]["lines_worst_case"] for b in program_lib.BLOCKS}
        sizes["single_row"] = plan["always_on"]["lines_base"] + max(
            plan[b]["lines_base"] + max([f["lines"] for f in plan[b]["files"] if "when" in f] or [0])
            for b in program_lib.BLOCKS if b != "always_on")
        out[cfg] = sizes
    return out


def core_files(man=None):
    man = man or manifest()
    return sorted({e["path"] for entries in man["core"].values() for e in entries})


def routing_rows():
    """The routing tables a model reads: the workflow's skill routing table and the
    playbook's "What loads with this file" table, as (base dir, row text) pairs."""
    rows = []
    for skill, heading in (("inbox-auto-draft-workflow", "## Skill routing"),
                           ("negotiation-playbook", "## What loads with this file")):
        text = read(os.path.join(SKILLS, skill, "SKILL.md"))
        section = text.split(heading, 1)[1].split("\n## ", 1)[0]
        rows += [(os.path.join(SKILLS, skill), line) for line in section.splitlines()
                 if line.startswith("|") or line.startswith("- **The load plan")]
    return rows


def resolve_route(base, ref):
    ref = ref if ref.endswith(".md") else ref + ".md"
    if ref.startswith("program/"):
        return os.path.join(PLUGIN, ref)
    if ref.startswith(("inbox-auto-draft-workflow/", "negotiation-playbook/")):
        return os.path.join(SKILLS, ref)
    if ref.startswith("shapes/"):
        return os.path.join(SKILLS, "inbox-auto-draft-workflow", "references", ref)
    return os.path.join(base, ref)


class Repo(unittest.TestCase):
    def test_manifests(self):
        m = json.loads(read(os.path.join(ROOT, ".claude-plugin", "marketplace.json")))
        p = json.loads(read(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))
        self.assertEqual(m["plugins"][0]["name"], p["name"])
        self.assertTrue(os.path.isdir(os.path.join(ROOT, m["plugins"][0]["source"])))
        json.loads(read(os.path.join(PLUGIN, "hooks", "hooks.json")))

    def test_skill_frontmatter(self):
        for name in os.listdir(SKILLS):
            path = os.path.join(SKILLS, name, "SKILL.md")
            if not os.path.exists(path):
                continue
            head = read(path).split("---")[1]
            self.assertIn(f"name: {name}", head, path)
            self.assertIn("description:", head, path)

    def test_tokens_defined(self):
        defined = set()
        for f in md_files(TEMPLATES):
            defined |= set(TOKEN.findall(read(f)))
        for f in list(md_files(SKILLS)) + list(md_files(PROGRAM)):  # packs and modules too
            if TEMPLATES in f or "rate-engine/references" in f:
                continue
            used = set(TOKEN.findall(read(f))) - LITERAL_OK
            prefix_ok = {t for t in used if t.startswith(("CRM_", "TBL_", "COL_", "WAREHOUSE_",
                                                          "LEAK_", "REGIME_", "CPM_", "GEO_"))}
            missing = used - defined - prefix_ok
            self.assertFalse(missing, f"{f}: undefined tokens {sorted(missing)}")

    def test_no_personal_voice_in_plugin(self):
        # The only voice that ships is the fictional example.
        for f in md_files(SKILLS):
            text = read(f)
            self.assertNotIn("He/him", text, f)

    def test_rule_registry(self):
        homes = {}
        for f in md_files(PLUGIN):
            for m in RULE.finditer(read(f)):
                homes.setdefault(m.group(1), []).append(os.path.relpath(f, PLUGIN))
                flags = set(m.group(2).split())
                self.assertLessEqual(flags, RULE_FLAGS, f"{f}: unknown rule flag {flags}")
        twice = {k: v for k, v in homes.items() if len(v) > 1}
        self.assertFalse(twice, f"rule defined in more than one place: {twice}")
        missing = REQUIRED_RULES - set(homes)
        self.assertFalse(missing, f"rule with no home: {sorted(missing)}")

    def test_overrides_are_declared(self):
        # Module > pack > core, and only through <!-- override:ID --> in program/ files,
        # on a rule its home marks `overridable`. Two default modules of one pack may not
        # override the same rule (the load plan would hold two answers).
        overridable = {m.group(1) for f in md_files(PLUGIN) for m in RULE.finditer(read(f))
                       if "overridable" in m.group(2).split()}
        by_file = {}
        for f in md_files(PLUGIN):
            ids = OVERRIDE.findall(read(f))
            if ids:
                self.assertTrue(rel(f).startswith("program/"), f"{rel(f)}: override outside program/")
                bad = set(ids) - overridable
                self.assertFalse(bad, f"{rel(f)}: overrides a rule that isn't overridable: {bad}")
                by_file[rel(f)] = set(ids)
        manifest = json.loads(read(os.path.join(PROGRAM, "manifest.json")))
        for pack_name, pack in manifest["packs"].items():
            seen = {}
            for mod in pack["default_modules"]:
                for entries in manifest["modules"][mod]["files"].values():
                    for e in entries:
                        for rid in by_file.get(e["path"], ()):
                            self.assertNotIn(rid, seen, f"{pack_name}: {mod} and {seen.get(rid)} "
                                                        f"both override {rid}")
                            seen[rid] = mod

    def test_executables(self):
        for rel in ("bin/inbox", "hooks/guard.py", "scripts/inbox.py"):
            self.assertTrue(os.access(os.path.join(PLUGIN, rel), os.X_OK), rel)


class Lean(unittest.TestCase):
    """The ratchet: sizes may shrink, never grow (tests/lean_baseline.json)."""

    @classmethod
    def setUpClass(cls):
        cls.now, cls.base = measure(), baseline()
        cls.allow = cls.base["spec_allowlist"]

    def no_growth(self, now, base, what):
        grew = {k: f"{base.get(k, 0)} -> {v}" for k, v in now.items() if v > base.get(k, 0)}
        self.assertFalse(grew, f"{what} grew past tests/lean_baseline.json: {grew}. Fold, "
                               "don't append; a genuinely new file needs a reviewed baseline entry.")

    def test_skill_md_lines(self):
        for name, lines in self.now["skill_lines"].items():
            if name not in self.allow["skill_md_over_500_lines"]:
                self.assertLessEqual(lines, SPEC_SKILL_LINES, f"{name}/SKILL.md: {lines} lines")
        self.no_growth(self.now["skill_lines"], self.base["skill_lines"], "SKILL.md lines")

    def test_description_length(self):
        for name, chars in self.now["description_chars"].items():
            if name not in self.allow["description_over_1024_chars"]:
                self.assertLessEqual(chars, SPEC_DESCRIPTION_CHARS, f"{name}: {chars} chars")
        self.no_growth(self.now["description_chars"], self.base["description_chars"],
                       "skill descriptions")
        self.assertLessEqual(self.now["description_total_chars"],
                             self.base["description_total_chars"])

    def test_spec_allowlist_only_shrinks(self):
        # An allowlisted skill that now meets the spec must leave the allowlist.
        for name in self.allow["skill_md_over_500_lines"]:
            self.assertGreater(self.now["skill_lines"].get(name, 0), SPEC_SKILL_LINES,
                               f"{name} meets the 500-line spec: remove it from the allowlist")
        for name in self.allow["description_over_1024_chars"]:
            self.assertGreater(self.now["description_chars"].get(name, 0), SPEC_DESCRIPTION_CHARS,
                               f"{name} meets the 1,024-char spec: remove it from the allowlist")

    def test_always_on_budget(self):
        now, base = self.now["always_on"], self.base["always_on"]
        self.assertLessEqual(now["lines"], base["lines"], f"always-on lines {now['lines']}")
        self.assertLessEqual(now["words"], base["words"], f"always-on words {now['words']}")
        for f, v in now["files"].items():
            b = base["files"].get(f, {"lines": 0, "words": 0})
            self.assertLessEqual(v["words"], b["words"], f"{f}: {v['words']} words")
            self.assertLessEqual(v["lines"], b["lines"], f"{f}: {v['lines']} lines")

    def test_file_budgets(self):
        self.no_growth(self.now["file_lines"], self.base["file_lines"], "skill file lines")
        self.assertLessEqual(self.now["file_lines_total"], self.base["file_lines_total"])

    def test_no_duplicate_text(self):
        self.no_growth(self.now["shared_12_word_runs"], self.base["shared_12_word_runs"],
                       "text shared between two files (12-word runs)")

    def test_baseline_is_current(self):
        # A shrink must lower the ceiling, or the room it freed can quietly fill up again.
        n, b = self.now, self.base
        pairs = {"skill file lines": (n["file_lines_total"], b["file_lines_total"]),
                 "always-on lines": (n["always_on"]["lines"], b["always_on"]["lines"]),
                 "always-on words": (n["always_on"]["words"], b["always_on"]["words"]),
                 "description chars": (n["description_total_chars"], b["description_total_chars"]),
                 "shared 12-word runs": (sum(n["shared_12_word_runs"].values()),
                                         sum(b["shared_12_word_runs"].values()))}
        stale = {k: f"{old} -> {new}" for k, (new, old) in pairs.items() if new < old}
        self.assertFalse(stale, f"sizes shrank but tests/lean_baseline.json still allows the old "
                                f"ceiling: {stale}. Run `python3 tests/test_repo.py --write-baseline` "
                                "and commit it with the change.")

    def test_block_load_plans(self):
        # Test 5: worst-case lines per block, neutral core and each built pack with its
        # default modules, stay under the manifest's block_budgets (the enforced
        # ceilings; block_targets holds the design goals they move toward).
        man = manifest()
        budgets = man["block_budgets"]
        for cfg, sizes in block_sizes(man).items():
            for block, lines in sizes.items():
                self.assertLessEqual(lines, budgets.get(cfg, {}).get(block, 0),
                                     f"{cfg} {block}: {lines} lines over its block budget")
                self.assertGreaterEqual(lines, budgets[cfg][block],
                                        f"{cfg} {block} shrank to {lines}: lock it in with "
                                        "`python3 tests/test_repo.py --write-baseline`")

    def test_block_budgets_within_targets(self):
        # The enforced ceilings never drift past the design goals (block_targets).
        man = manifest()
        for cfg, sizes in man["block_budgets"].items():
            for block, lines in sizes.items():
                self.assertLessEqual(lines, man["block_targets"][cfg][block],
                                     f"{cfg} {block}: {lines} lines over its design target")

    def test_manifest_triggers(self):
        # Lean load plan: a built pack's default modules are built; every pack and
        # module file loads on a `when` unless it is the pack's base or always needed;
        # `base_if` names a real program answer (or a mode a pack gives that module)
        # and only sits on a file that also has its `when`.
        man = manifest()
        modes = {}
        for pack in man["packs"].values():
            for mod, mode in pack["default_modules"].items():
                modes.setdefault(mod, set()).add(mode)
        for rules in man["modifiers"].values():
            for r in rules.values():
                for mod, mode in r.get("mode", {}).items():
                    modes.setdefault(mod, set()).add(mode)
        for name, pack in man["packs"].items():
            if pack["status"] == "built":
                for mod in pack["default_modules"]:
                    self.assertEqual(man["modules"][mod]["status"], "built", f"{name}: {mod}")
        for name, mod in man["modules"].items():
            if mod["status"] == "built":
                self.assertTrue(any(mod["files"].values()), f"{name} is built but has no files")
            for block, entries in mod["files"].items():
                for e in entries:
                    self.assertIn("when", e, f"{e['path']} ({block}) loads every time: give it a `when`")
                    for b in e.get("base_if", []):
                        key, _, value = b.partition(": ")
                        ok = (key == "mode" and value in modes.get(name, set())) or \
                            value in program_lib.PROGRAM_KEYS.get(key, set())
                        self.assertTrue(ok, f"{e['path']}: base_if {b!r} is no program answer")

    def test_core_vocabulary(self):
        # Test 8: the core loads for every program, so it carries no pack or module words.
        found = {}
        for path in core_files():
            allow = CORE_ALLOW.get(path, set())
            for n, line in enumerate(read(os.path.join(PLUGIN, path)).splitlines(), 1):
                hits = {m.group(0).lower() for m in CORE_DENY_CI.finditer(line)}
                hits |= {m.group(0) for m in CORE_DENY_CS.finditer(line)}
                hits = {h for h in hits if not any(h.startswith(a) for a in allow)}
                if hits:
                    found.setdefault(path, []).append(f"{n}: {sorted(hits)}")
        self.assertFalse(found, f"pack or module vocabulary in core files: {found}")

    def test_routing_targets_exist(self):
        # Test 9: every file a routing row names exists; every core manifest file is
        # named by a routing row (or the always-on line); every pack and module file is
        # reached through the load plan, which a routing row points at; no program/
        # file is left out of the manifest.
        man = manifest()
        rows = routing_rows()
        text = "\n".join(r for _, r in rows)
        for base, row in rows:
            for ref in ROUTING_PATH.findall(row):
                self.assertTrue(os.path.isfile(resolve_route(base, ref)), f"{ref} in: {row}")
        always = read(os.path.join(WORKFLOW, "SKILL.md")).split("**Always loaded", 1)[1][:400]
        router = rel(os.path.join(WORKFLOW, "SKILL.md"))
        for path in core_files(man):
            if path == router:
                continue
            parts = path.split("/")
            if parts[-1] == "SKILL.md":
                named = f"`{parts[1]}`" in text or f"`{parts[1]}`" in always
            else:
                stem = "/".join(parts[-2:]).removesuffix(".md")
                named = stem in text or stem in always
            self.assertTrue(named, f"{path} is in the manifest but no routing row names it")
        self.assertIn("load plan", text, "no routing row points at the load plan")
        listed = {e["path"] for src in [p["files"] for p in man["packs"].values()] +
                  [m["files"] for m in man["modules"].values()]
                  for entries in src.values() for e in entries}
        for f in md_files(PROGRAM):
            self.assertIn(rel(f), listed, f"{rel(f)} is not in the manifest")

    def test_no_phrasebooks(self):
        new = set(self.now["phrasebook_headings"]) - set(self.base["phrasebook_headings"])
        self.assertFalse(new, f"new phrasebook / sent-diff headings: {sorted(new)}")


def write_baseline():
    old = baseline() if os.path.exists(BASELINE) else {}
    out = {"_about": "Lean ratchet for tests/test_repo.py (Lean). Measured sizes; tests fail "
                     "if anything grows. Lower them with `python3 tests/test_repo.py "
                     "--write-baseline`. spec_allowlist is edited by hand and only shrinks.",
           "spec_allowlist": old.get("spec_allowlist", {"skill_md_over_500_lines": [],
                                                         "description_over_1024_chars": []})}
    out.update(measure())
    with open(BASELINE, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, sort_keys=False)
        f.write("\n")
    print("wrote", BASELINE)
    # The manifest's per-block ceilings ratchet the same way (one line, rewritten in place).
    path = os.path.join(PROGRAM, "manifest.json")
    text = read(path)
    line = '  "block_budgets": ' + json.dumps(block_sizes()) + ","
    text, n = re.subn(r'(?m)^  "block_budgets": .*,$', lambda _: line, text)
    assert n == 1, "manifest.json has no block_budgets line"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote block_budgets in", path)


if __name__ == "__main__":
    if "--write-baseline" in sys.argv:
        write_baseline()
    else:
        unittest.main()
