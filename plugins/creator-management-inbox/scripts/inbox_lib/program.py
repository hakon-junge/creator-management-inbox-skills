"""How the user's program works, and what it loads.

Reads the ```program block in profile/program.md, validates each answer, then
resolves it against program/manifest.json:

    pack     = the `business:` answer (unset, TODO or a planned pack = no pack)
    modules  = the pack's default modules, then the other answers (modifiers),
               then an optional `modules: +x, -y` line, then `requires` guards
    load plan = core + pack + module files, per block, with line counts

Deterministic and stdlib-only, so `inbox program` gives the same answer every run.
"""
import json
import os
import re

from .money import parse_number

# Allowed values per program.md key. `mix` is an alias, and only for `model`.
PROGRAM_KEYS = {
    "business": {"ecommerce", "saas", "b2b"},
    "model": {"always-on", "campaigns", "seasonal", "mix"},
    "budget": {"per-creator", "monthly-pot", "campaign-pot", "no-cash"},
    "success": {"sales", "signups", "reach", "content", "pipeline"},
    "pricing": {"views", "rate-card", "their-quote", "commission", "gifting"},
    "deal_shape": {"test-then-scale", "one-off", "ambassador"},
    "creator_types": {"influencers", "ugc", "affiliates", "agency-talent", "podcasters",
                      "newsletters"},
}
REQUIRED = ("model", "budget", "success", "pricing", "deal_shape")  # the five questions
SINGLE = {"business", "success"}                                     # one value only
BLOCKS = ("always_on", "block_1", "block_2", "block_3")

_UNSET = re.compile(r"^(|todo\b.*|none)$", re.I)


def read_block(text):
    """{key: raw value} from the ```program block (comments stripped)."""
    m = re.search(r"```program\s*\n(.*?)```", text, re.S)
    vals = {}
    for raw in (m.group(1) if m else "").splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" in line:
            k, v = [x.strip() for x in line.split(":", 1)]
            vals[k] = v
    return vals


def split(value):
    return [v.strip().lower() for v in re.split(r"[,\s]+", value or "") if v.strip()]


def validate(vals):
    """Parse comma lists and check every value on its own.
    Returns (parsed {key: [values]}, problems {key: why})."""
    parsed, problems = {}, {}
    for key, allowed in PROGRAM_KEYS.items():
        raw = vals.get(key, "")
        if _UNSET.match(raw.strip()):
            if key in REQUIRED:
                problems[key] = raw or "missing"
            continue
        items = split(raw)
        bad = [v for v in items if v not in allowed]
        if bad:
            problems[key] = f"unknown: {', '.join(bad)}" + (
                " (mix only works for model)" if "mix" in bad else "")
            continue
        if key in SINGLE and len(items) > 1:
            problems[key] = "one value only"
            continue
        if key == "model" and "mix" in items:
            i = items.index("mix")
            items[i:i + 1] = [x for x in ("always-on", "campaigns") if x not in items]
        parsed[key] = list(dict.fromkeys(items))
    return parsed, problems


def module_switches(raw, known):
    """`modules: +exclusivity, -usage-rights` -> ([on], [off], [unknown])."""
    on, off, unknown = [], [], []
    for tok in split(raw):
        name = tok.lstrip("+-")
        if name not in known:
            unknown.append(tok)
        elif tok.startswith("-"):
            off.append(name)
        else:
            on.append(name)
    return on, off, unknown


def affiliate_program(profile_dir):
    """'none' when affiliate.md says there is no program, 'unset' while TODO
    or missing, else 'yes'."""
    try:
        with open(os.path.join(profile_dir, "affiliate.md"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return "unset"
    m = re.search(r"^\s*-\s*Program:\s*(.+)$", text, re.M)
    value = m.group(1).strip().strip("`").lower() if m else ""
    if value.startswith("none"):
        return "none"
    return "unset" if (not value or value.startswith("todo")) else "yes"


def _profile_value(text, token):
    m = re.search(r"`\{\{" + token + r"\}\}`:\s*(.+)", text)
    return m.group(1).strip() if m else ""


def _amount(value):
    m = re.match(r"\D{0,4}?(\d[\d,.]*\d|\d)", value or "")
    try:
        return parse_number(m.group(1)) if m else None
    except ValueError:
        return None


def campaign_cap(profile_dir):
    """(cap, why) when program.md prices from a campaign pot (`budget: campaign-pot`)
    and `{{CAMPAIGN_BUDGET}}` holds a number: the pot, or the pot's share per creator
    when `{{CREATORS_PER_CAMPAIGN}}` is a number too. Else None."""
    try:
        with open(os.path.join(profile_dir, "program.md"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    parsed, _ = validate(read_block(text))
    pot = _amount(_profile_value(text, "CAMPAIGN_BUDGET"))
    if "campaign-pot" not in parsed.get("budget", []) or not pot:
        return None
    n = _amount(_profile_value(text, "CREATORS_PER_CAMPAIGN"))
    if n and n >= 1:
        return pot / n, f"campaign budget {pot:,.0f} / {n:.0f} creators"
    return pot, f"campaign budget {pot:,.0f}"


def load_manifest(plugin_root):
    with open(os.path.join(plugin_root, "program", "manifest.json"), encoding="utf-8") as f:
        return json.load(f)


def resolve(parsed, module_line, manifest, profile_dir):
    """Pick the pack and the modules. Each module carries the answers that
    switched it on, so a user can see why something loads."""
    warnings, mods, offs = [], {}, []
    modules = manifest["modules"]

    def on(name, why, mode=None):
        m = mods.setdefault(name, {"name": name, "on_by": [], "mode": None,
                                   "status": modules[name]["status"]})
        if why not in m["on_by"]:
            m["on_by"].append(why)
        if mode:
            m["mode"] = mode

    business = (parsed.get("business") or [None])[0]
    pack = manifest["packs"].get(business) if business else None
    pack_name = business if pack and pack["status"] != "planned" else None
    if not business:
        warnings.append("business not set: core only, no pack - say 'set up my program'")
    elif not pack_name:
        warnings.append(f"the {business} pack is planned, not built yet: core plus the "
                        "modules your other answers switch on")
    if pack_name:
        for name, mode in pack["default_modules"].items():
            on(name, f"pack default ({pack_name})", mode)

    variants = []
    for key in ("model", "budget", "success", "pricing", "deal_shape", "creator_types"):
        for value in parsed.get(key, []):
            rule = manifest["modifiers"][key].get(value, {})
            why = f"{key}: {value}"
            if "variant" in rule:
                variants.append((rule["variant"], why))
            for name in rule.get("on", []):
                on(name, why, rule.get("mode", {}).get(name))
            offs += [(name, why) for name in rule.get("off", [])]
            by_pack = rule.get("on_by_pack", {})
            for name in by_pack.get(business or "", by_pack.get("*", [])):
                on(name, why)
    if variants:  # an explicit model/budget answer replaces the pack's default variant
        chosen = {v for v, _ in variants}
        for name in [n for n in mods if modules[n].get("group") == "budget-model"]:
            if name not in chosen:
                mods.pop(name)
        for name, why in variants:
            on(name, why)

    plus, minus, unknown = module_switches(module_line, modules)
    for name in plus:
        on(name, f"modules: +{name}")
    offs += [(name, f"modules: -{name}") for name in minus]

    for name in list(mods):
        if modules[name].get("requires") == "affiliate":
            state = affiliate_program(profile_dir)
            if state == "none":
                offs.append((name, "affiliate.md says none"))
            elif state == "unset":
                warnings.append("affiliate.md not filled: commission terms stay out of drafts")
    off = []
    for name, why in offs:  # switches off win over switches on
        if mods.pop(name, None):
            off.append({"name": name, "off_by": why})

    order = list(modules)
    active = sorted(mods.values(), key=lambda m: order.index(m["name"]))
    binding = None
    if len([m for m in active if modules[m["name"]].get("group") == "budget-model"]) > 1:
        binding = manifest["thread_binding"]
    return {"pack": pack_name, "modules": active, "off": off, "unknown": unknown,
            "warnings": warnings, "thread_binding": binding}


def load_plan(manifest, plugin_root, pack_name, active, pricing):
    """Files per block with line counts. Paths are relative to the plugin root,
    which `inbox program` prints once as `plugin_root`, so every run's output
    stays short. `lines_base` = what the block always loads; `lines_worst_case`
    adds every on-trigger file (those carry `when`). A module file's `base_if`
    lists program answers ("mode: lead", "budget: no-cash") that make it load
    every time (`base_by` says which). `from` names the pack or module that
    added a file."""
    sources = [("core", manifest["core"], None)]
    if pack_name:
        sources.append((f"pack:{pack_name}", manifest["packs"][pack_name]["files"], None))
    for m in active:
        sources.append((f"module:{m['name']}", manifest["modules"][m["name"]]["files"], m))
    plan, missing = {}, []
    for block in BLOCKS:
        files = []
        for origin, src, mod in sources:
            for entry in src.get(block, []):
                skip = entry.get("skip_if_pricing_only")
                if skip and pricing and set(pricing) <= set(skip):
                    continue
                path = os.path.join(plugin_root, entry["path"])
                try:
                    with open(path, encoding="utf-8") as f:
                        lines = len(f.read().splitlines())
                except OSError:
                    lines = None
                    missing.append(entry["path"])
                f = {"path": entry["path"], "lines": lines}
                why = mod and ({f"mode: {mod.get('mode')}"} | set(mod.get("on_by", [])))
                base_by = [b for b in entry.get("base_if", []) if why and b in why]
                if base_by:                 # this program loads it every time
                    f["base_by"] = base_by[0]
                elif entry.get("when"):     # loaded only on this trigger
                    f["when"] = entry["when"]
                if origin != "core":
                    f["from"] = origin
                files.append(f)
        plan[block] = {
            "lines_base": sum(f["lines"] or 0 for f in files if "when" not in f),
            "lines_worst_case": sum(f["lines"] or 0 for f in files),
            "files": files}
    return plan, missing
