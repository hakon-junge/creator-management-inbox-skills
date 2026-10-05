"""Tests for the Your Voice plugin: manifests, skill budgets, the default voice and
the voice.py helper.

Run from the repo root:  python3 -m unittest discover -s tests -v
No network and no real voice home: every run uses a throwaway VOICE_HOME (and a
throwaway INBOX_HOME, so the inbox-import check never reads a real profile).
Fixtures in tests/fixtures/voice/ are fictional.
"""
import codecs
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "your-voice")
SKILLS = os.path.join(PLUGIN, "skills")
APPLY = os.path.join(SKILLS, "your-voice")
BUILDER = os.path.join(SKILLS, "your-voice-builder")
VOICE_PY = os.path.join(BUILDER, "scripts", "voice.py")
# The copy voice.py reads (identical to the apply skill's, see Copies).
DEFAULT_VOICE = os.path.join(SKILLS, "your-voice-builder", "references", "default-voice.md")
TEMPLATE = os.path.join(APPLY, "references", "voice-template.md")
FIX = os.path.join(ROOT, "tests", "fixtures", "voice")
INBOX_DEMO = os.path.join(ROOT, "plugins", "creator-management-inbox", "demo", "profile")
ME = "robin@northpeak.example"

# Line budgets from the spec; descriptions stay under 900 characters (hard cap 1,024).
LINE_BUDGETS = {
    "your-voice/SKILL.md": 150,
    "your-voice-builder/SKILL.md": 220,
    "your-voice/references/default-voice.md": 160,
    "your-voice/references/voice-template.md": 80,
    "your-voice-builder/references/analysis.md": 140,
}
DESCRIPTION_MAX = 900

# Markers of a real person's or company's voice that must never ship. Stored
# rot13-encoded so the private words themselves never appear in this public repo.
PRIVATE_MARKERS = [codecs.decode(w, "rot13") for w in (
    "Xvggy", "Lhyvvn", "Gvcnygv", "NV Gbxraf", "Oenaq Fghqvb", "jbj jbj jbj",
    "Gnyx fbba", "Fcrnx fbba", "erfuncrq jnl sbejneq", "Ab cerffher rvgure jnl",
    "dhvpx purpx-va sebz zl fvqr", "Gunaxf fb zhpu ~")]
HEARTS = ("\u2764\u2665\U0001F49B\U0001F499\U0001F49A\U0001F49C\U0001F9E1\U0001F5A4"
          "\U0001F90D\U0001F90E\U0001FA77\U0001FA75\U0001FA76\U0001F495\U0001F496"
          "\U0001F497\U0001F498\U0001F49D\U0001F49E\U0001F970\U0001F60D\U0001FAF6\U0001FAC2")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_voice_module():
    spec = importlib.util.spec_from_file_location("voice", VOICE_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


voice = load_voice_module()


def frontmatter(path):
    """name and description of a SKILL.md (description may be a folded block)."""
    head = read(path).split("---")[1]
    out, key = {}, None
    for line in head.splitlines():
        m = re.match(r"^([a-z_-]+):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            out[key] = "" if val in (">", "|", ">-", "|-") else val
        elif key and line.strip():
            out[key] = (out[key] + " " + line.strip()).strip()
    return out


def demo_names():
    """People and companies in the inbox plugin's demo: none may leak into the
    default voice."""
    names = {"Fernwell", "Sam", "Rivera", "Maya", "Ortiz", "Jonas", "Weber", "Jordan",
             "Priya", "Nair", "Ava", "Chen", "Leo", "Leo Grant", "QuickReach", "Quickreach"}
    for rel in ("me.md", "company.md"):
        m = re.search(r"`\{\{(OPERATOR_NAME|COMPANY)\}\}`:\s*(.+)", read(os.path.join(INBOX_DEMO, rel)))
        if m:
            names |= set(m.group(2).split())
    for f in os.listdir(os.path.join(INBOX_DEMO, "creators")):
        first = os.path.splitext(f)[0].split("-")[0]
        names.add(first.capitalize())
    return names


class Tmp:
    """A throwaway voice home (and inbox home) for one test."""

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="voice-test-")
        self.home = os.path.join(self.root, "home")
        self.inbox = os.path.join(self.root, "inbox")

    def run(self, *args, stdin=None):
        env = {**os.environ, "VOICE_HOME": self.home, "INBOX_HOME": self.inbox}
        p = subprocess.run([sys.executable, VOICE_PY, *args], capture_output=True,
                           text=True, input=stdin, env=env)
        try:
            return p.returncode, json.loads(p.stdout)
        except ValueError:
            return p.returncode, p.stdout + p.stderr

    def samples(self, path):
        with open(path, encoding="utf-8") as f:
            return [json.loads(l) for l in f if l.strip()]

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class Manifests(unittest.TestCase):
    def test_plugin_json(self):
        p = json.loads(read(os.path.join(PLUGIN, ".claude-plugin", "plugin.json")))
        self.assertEqual(p["name"], "your-voice")
        self.assertEqual(p["displayName"], "Your Voice")
        self.assertRegex(p["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(p["license"], "MIT")
        self.assertEqual(p["author"]["name"], "Fluencrs")

    def test_marketplace_entry(self):
        m = json.loads(read(os.path.join(ROOT, ".claude-plugin", "marketplace.json")))
        entries = {e["name"]: e for e in m["plugins"]}
        self.assertIn("creator-management-inbox", entries)
        e = entries["your-voice"]
        self.assertEqual(e["source"], "./plugins/your-voice")
        self.assertEqual(e["category"], "productivity")
        self.assertTrue(os.path.isdir(os.path.join(ROOT, e["source"])))

    def test_portable_layout(self):
        # Works in Claude Code, Cowork and Claude.ai: no top-level bin/, no hooks.
        for name in ("bin", "hooks"):
            self.assertFalse(os.path.exists(os.path.join(PLUGIN, name)), name)
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, "README.md")))


class Skills(unittest.TestCase):
    def test_frontmatter_and_description_length(self):
        for name in ("your-voice", "your-voice-builder"):
            fm = frontmatter(os.path.join(SKILLS, name, "SKILL.md"))
            self.assertEqual(fm.get("name"), name)
            desc = fm.get("description", "")
            self.assertGreater(len(desc), 100, name)
            self.assertLessEqual(len(desc), DESCRIPTION_MAX, f"{name}: {len(desc)} chars")

    def test_names_differ_from_inbox_skills(self):
        inbox = set(os.listdir(os.path.join(ROOT, "plugins", "creator-management-inbox",
                                            "skills")))
        self.assertIn("comms-style", inbox)
        self.assertFalse({"your-voice", "your-voice-builder"} & inbox)

    def test_line_budgets(self):
        for rel, limit in LINE_BUDGETS.items():
            n = len(read(os.path.join(SKILLS, rel)).splitlines())
            self.assertLessEqual(n, min(limit, 500), f"{rel}: {n} lines > {limit}")

    def test_referenced_files_exist(self):
        for rel in ("your-voice/references/default-voice.md",
                    "your-voice/references/voice-template.md",
                    "your-voice-builder/references/analysis.md",
                    "your-voice-builder/scripts/voice.py"):
            self.assertTrue(os.path.isfile(os.path.join(SKILLS, rel)), rel)


class Copies(unittest.TestCase):
    def test_builder_copies_match(self):
        # Each skill must work when uploaded alone, so the builder keeps its own copies.
        for name in ("default-voice.md", "voice-template.md"):
            with open(os.path.join(SKILLS, "your-voice", "references", name), encoding="utf-8") as a, \
                    open(os.path.join(SKILLS, "your-voice-builder", "references", name), encoding="utf-8") as b:
                self.assertEqual(a.read(), b.read(), f"{name}: the two copies differ - edit both")

    def test_no_paths_into_the_other_skill(self):
        with open(os.path.join(SKILLS, "your-voice-builder", "SKILL.md"), encoding="utf-8") as f:
            self.assertNotIn("../your-voice/", f.read())


class DefaultVoice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(DEFAULT_VOICE)

    def test_labelled(self):
        self.assertIn("Default voice - used until you build your own", self.text)

    def test_has_every_template_section(self):
        sections = re.findall(r"(?m)^## (.+)$", read(TEMPLATE))
        self.assertGreaterEqual(len(sections), 8)
        for s in sections:
            self.assertRegex(self.text, r"(?m)^## " + re.escape(s) + r"\s*$", s)

    def test_template_front_matter_and_house_style(self):
        fm = voice.front_matter(read(TEMPLATE))
        for key in ("name", "built", "refreshed", "sources", "samples"):
            self.assertIn(key, fm)
        for path in (TEMPLATE, DEFAULT_VOICE):
            self.assertRegex(read(path), r"```house-style\n")
        hs = voice.house_style(self.text)
        self.assertEqual(hs["em_dashes"], "replace")
        self.assertIn("to be honest", voice.banned_words(hs))

    def test_no_personal_names_brands_or_catchphrases(self):
        for name in demo_names():
            self.assertNotRegex(self.text, r"\b" + re.escape(name) + r"\b", name)
        for f in os.listdir(os.path.join(SKILLS)):
            for d, _, fs in os.walk(os.path.join(SKILLS, f)):
                for fn in fs:
                    if fn.endswith((".md", ".py")):
                        body = read(os.path.join(d, fn)).lower()
                        hits = [m for m in PRIVATE_MARKERS if m.lower() in body]
                        self.assertFalse(hits, f"{fn}: private marker(s) {hits}")
        self.assertIsNone(re.search(r"([A-Za-z])\1{3,}", self.text), "stretched word")
        self.assertFalse(set(HEARTS) & set(self.text), "heart emoji")
        self.assertFalse(voice.EMOJI.findall(self.text), "emoji in the default voice")

    def test_practises_its_own_house_style(self):
        self.assertNotIn("—", self.text)
        self.assertNotIn("–", self.text)


class Import(unittest.TestCase):
    def setUp(self):
        self.t = Tmp()

    def tearDown(self):
        self.t.cleanup()

    def import_(self, *paths, extra=()):
        out = os.path.join(self.t.root, "s.jsonl")
        code, res = self.t.run("import", *paths, "--me", ME, "--out", out, *extra)
        self.assertEqual(code, 0, res)
        return res, self.t.samples(out)

    def test_spoofed_display_name_excluded(self):
        res, samples = self.import_(os.path.join(FIX, "mail", "spoofed-quoted.eml"),
                                    os.path.join(FIX, "mail", "spoofed-bare.eml"))
        self.assertEqual(samples, [])
        self.assertEqual(res["skipped"]["not_from_me"], 2)

    def test_sender_rule_unit(self):
        c = voice.Collector({ME}, None)
        self.assertTrue(c.sender_is_me("Robin Vale <Robin@NorthPeak.example>"))
        self.assertTrue(c.sender_is_me(ME))
        for spoof in ('"robin@northpeak.example" <spoof@elsewhere.example>',
                      "robin@northpeak.example <spoof@elsewhere.example>",
                      "robin@northpeak.example)<spoof@elsewhere.example>",
                      "spoof@elsewhere.example (robin@northpeak.example)",
                      "Someone <spoof@elsewhere.example>, robin@northpeak.example",
                      "robin@northpeak.example.elsewhere.example"):
            self.assertFalse(c.sender_is_me(spoof), spoof)

    def test_mail_folder(self):
        res, samples = self.import_(os.path.join(FIX, "mail"))
        text = "\n".join(s["text"] for s in samples)
        for marker in ("SPOOFMARKER", "FORGEDMARKER", "OTHERPERSONMARKER", "QUOTEDMARKER",
                       "SIGNATUREMARKER", "FORWARDEDMARKER", "AUTOREPLYMARKER",
                       "UNVERIFIEDMARKER", "HTMLPARTMARKER"):
            self.assertNotIn(marker, text, marker)
        self.assertEqual(len(samples), 5)
        self.assertTrue(all(s["channel"] == "email" for s in samples))
        self.assertEqual(set(samples[0]), {"channel", "date", "text"})
        self.assertEqual(samples[0]["date"], "2026-09-20")  # newest first
        sk = res["skipped"]
        self.assertEqual(sk["not_in_sent"], 1)       # forged From, inbox label
        self.assertEqual(sk["auto_reply"], 1)
        self.assertEqual(sk["under_15_words"], 1)
        self.assertEqual(sk["unverified_sender"], 1)
        self.assertEqual(sk["not_from_me"], 4)
        self.assertIn("Let me know which dates suit you best.", text)
        self.assertIn("The second section is the part I would love your eyes on.", text)
        self.assertIn("Great script. The opening question lands", text)  # html-only mail

    def test_quote_and_signature_stripping_unit(self):
        body = ("Thanks, Thursday works and I will send the brief the same day so you "
                "have time.\n\nOn Mon, 21 Sep 2026 at 10:02, Someone <s@x.example>\n"
                "wrote:\n> old text\n")
        self.assertNotIn("old text", voice.strip_quotes(body))
        self.assertNotIn("Signature", voice.strip_quotes("Hi\n\nBody here.\n-- \nSignature"))
        self.assertNotIn("quoted", voice.strip_quotes("Mine.\n> quoted\nMore mine."))
        own = "On Monday we met about the brief.\nThis is what I wrote:\nThe draft itself."
        self.assertEqual(voice.strip_quotes(own), own)  # no date, no address: not a quote

    def test_slack_linkedin_and_text(self):
        res, samples = self.import_(os.path.join(FIX, "slack"), os.path.join(FIX, "linkedin"),
                                    os.path.join(FIX, "text"),
                                    extra=("--name", "Robin Vale", "--channel", "email"))
        by = {}
        for s in samples:
            by.setdefault(s["channel"], []).append(s["text"])
        self.assertEqual(len(by["slack"]), 2)        # a 2-message burst merged, a recap
        self.assertEqual(len(by["linkedin"]), 2)     # the one-line post dropped
        self.assertEqual(len(by["email"]), 2)        # --- separated text samples
        joined = "\n".join(by["slack"])
        self.assertIn("Need a decision on the October slot by Friday.\nOption 1", joined)
        self.assertIn("@[Name]", joined)
        self.assertIn("See the brief.", joined)
        self.assertNotIn("OTHERPERSONMARKER", joined)
        self.assertNotIn("has joined", joined)
        self.assertEqual(res["skipped"]["under_15_words"], 3)

    def test_slack_needs_name(self):
        res, samples = self.import_(os.path.join(FIX, "slack"))
        self.assertEqual(samples, [])
        self.assertIn("slack_needs_name", res["skipped"])

    def test_since(self):
        res, samples = self.import_(os.path.join(FIX, "mail"), extra=("--since", "2026-09-15"))
        self.assertEqual([s["date"] for s in samples], ["2026-09-20", "2026-09-16", "2026-09-15"])
        self.assertEqual(res["skipped"]["before_since"], 2)


class Stats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = Tmp()
        code, cls.res = cls.t.run("stats", os.path.join(FIX, "stats.jsonl"))
        assert code == 0, cls.res

    @classmethod
    def tearDownClass(cls):
        cls.t.cleanup()

    def test_email_frequencies(self):
        e = self.res["channels"]["email"]
        self.assertEqual(e["count"], 4)
        self.assertEqual(e["share_with_greeting"], 0.75)
        self.assertEqual(e["greetings"][0], {"text": "Hi [Name],", "count": 2, "share": 0.5})
        self.assertEqual(e["share_with_emoji"], 0.25)
        self.assertEqual(e["top_emoji"][0]["count"], 1)
        self.assertEqual(e["share_with_exclamation"], 0.25)
        self.assertEqual(e["em_dashes"], 1)
        self.assertEqual(e["median_paragraphs"], 3.0)
        self.assertEqual(e["openers"][0], {"text": "Thanks for sending", "count": 2, "share": 0.5})
        self.assertEqual(e["closers"][0]["count"], 3)
        self.assertEqual(e["share_typed_name"], 0.33)
        self.assertEqual(e["recurring_phrases"][0],
                         {"text": "let me know which dates suit you best", "samples": 3})

    def test_linkedin_and_overall(self):
        li = self.res["channels"]["linkedin"]
        self.assertEqual(li["count"], 2)
        self.assertEqual(li["share_with_bullets"], 0.5)
        self.assertEqual(li["share_with_greeting"], 0.0)
        self.assertEqual(self.res["channels"]["all"]["count"], 6)


class Check(unittest.TestCase):
    def setUp(self):
        self.t = Tmp()

    def tearDown(self):
        self.t.cleanup()

    def test_dashes_and_banned_words_but_not_urls_or_code(self):
        code, r = self.t.run("check", os.path.join(FIX, "check-input.txt"),
                             "--voice", os.path.join(FIX, "voice.md"))
        self.assertEqual(code, 0, r)
        text = r["text"]
        self.assertTrue(text.startswith("To be direct - the plan works. I’ll be direct with you"))
        self.assertIn("follow up on 10-12 March", text)
        self.assertIn("\nThe brief is final.", text)               # phrase removed, capital kept
        self.assertIn("https://docs.northpeak.example/to-be-honest—guide", text)
        self.assertIn("`code — kept`", text)
        self.assertEqual(len(r["warnings"]), 2)                     # "!" and emoji
        self.assertTrue(r["changed"])

    def test_default_voice_used_without_voice_md(self):
        code, r = self.t.run("check", "-", stdin="Fine — to be honest, it works.")
        self.assertEqual(r["voice"], os.path.normpath(DEFAULT_VOICE))
        self.assertEqual(r["text"], "Fine - to be direct, it works.")


class Home(unittest.TestCase):
    def setUp(self):
        self.t = Tmp()

    def tearDown(self):
        self.t.cleanup()

    @unittest.skipIf(os.name == "nt", "POSIX permissions")
    def test_private_home(self):
        code, r = self.t.run("init")
        self.assertEqual(code, 0, r)
        for d in (self.t.home, os.path.join(self.t.home, "samples")):
            self.assertEqual(os.stat(d).st_mode & 0o777, 0o700, d)
        loose = os.path.join(self.t.home, "voice.md")
        with open(loose, "w") as f:
            f.write("x")
        os.chmod(loose, 0o644)
        code, r = self.t.run("init")
        self.assertIn("voice.md", r["tightened"])
        self.assertEqual(os.stat(loose).st_mode & 0o777, 0o600)
        code, r = self.t.run("import", os.path.join(FIX, "text"), "--me", ME)
        self.assertEqual(os.stat(r["out"]).st_mode & 0o777, 0o600)
        self.assertEqual(os.stat(os.path.dirname(r["out"])).st_mode & 0o777, 0o700)

    def test_where_and_clean(self):
        code, r = self.t.run("where")
        self.assertFalse(r["exists"])
        self.assertFalse(r["inbox_voice"]["exists"])
        self.t.run("init")
        shutil.copy(os.path.join(FIX, "voice.md"), os.path.join(self.t.home, "voice.md"))
        code, r = self.t.run("where")
        self.assertTrue(r["exists"])
        self.assertEqual(r["front_matter"]["name"], "Robin Vale")
        self.assertTrue(r["stale"])
        self.t.run("import", os.path.join(FIX, "text"), "--me", ME)
        self.assertTrue(os.path.isdir(os.path.join(self.t.home, "build")))
        code, r = self.t.run("clean")
        self.assertFalse(os.path.exists(os.path.join(self.t.home, "build")))

    def test_inbox_voice_detected_only_when_filled(self):
        prof = os.path.join(self.t.inbox, "profile")
        os.makedirs(prof)
        shutil.copy(os.path.join(ROOT, "plugins", "creator-management-inbox", "skills",
                                 "company-context", "templates", "voice.md"),
                    os.path.join(prof, "voice.md"))
        code, r = self.t.run("where")
        self.assertEqual(r["inbox_voice"], {"path": os.path.join(prof, "voice.md"),
                                            "exists": True, "filled": False})
        shutil.copy(os.path.join(INBOX_DEMO, "voice.md"), os.path.join(prof, "voice.md"))
        code, r = self.t.run("where")
        self.assertTrue(r["inbox_voice"]["filled"])


if __name__ == "__main__":
    unittest.main()
