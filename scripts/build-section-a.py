#!/usr/bin/env python3
"""Build FP Section A pages from one Focus Star source file."""

from __future__ import annotations

import json
import re
from html import escape, unescape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "assets" / "focus-star" / "section-a.source.json"
CONFIG_JSON_PATH = ROOT / "assets" / "focus-star" / "config.json"
CONFIG_JS_PATH = ROOT / "assets" / "focus-star" / "config.js"
AI_CONTEXT_PATH = ROOT / "assets" / "focus-star" / "section-a.ai-context.json"

PAGE_ORDER = ("product", "people", "purpose", "promise", "personality")


def load_source() -> dict[str, Any]:
    data = json.loads(SOURCE_PATH.read_text())
    errors: list[str] = []
    if not isinstance(data.get("pillars"), list):
        errors.append("source must contain pillars[]")
    else:
        ids = [pillar.get("id") for pillar in data["pillars"]]
        if ids != list(PAGE_ORDER):
            errors.append(f"pillars must be ordered {PAGE_ORDER}, got {ids}")
        for pillar in data["pillars"]:
            case = pillar.get("case") or {}
            contract = case.get("contract") or {}
            for key in (
                "strategic_question",
                "core_decision",
                "plain_meaning",
                "page_thesis",
                "rules_in",
                "rules_out",
                "tradeoff",
                "proof_required",
                "output_controls",
            ):
                if key not in contract:
                    errors.append(f"{pillar.get('id')}.case.contract.{key} is required")
    if errors:
        raise SystemExit("\n".join(errors))
    return data


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n")
    print(f"wrote {path.relative_to(ROOT)}")


def strip_tags(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", value))


def esc(value: Any) -> str:
    return escape(str(value), quote=True)


def list_html(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def card(title: str, label: str, body: str | list[str], dark: bool = False) -> str:
    body_html = list_html(body) if isinstance(body, list) else f"<p>{esc(body)}</p>"
    class_name = "p-card dark" if dark else "p-card"
    return f"""
      <article class="{class_name}">
        <div class="p-card-label">{esc(label)}</div>
        <h3>{esc(title)}</h3>
        {body_html}
      </article>
    """


def row(title: str, body: str | list[str]) -> str:
    body_html = list_html(body) if isinstance(body, list) else f"<p>{esc(body)}</p>"
    return f"""
      <div class="p-row">
        <h3>{esc(title)}</h3>
        {body_html}
      </div>
    """


def section(num: str, kicker: str, title: str, desc: str, body: str) -> str:
    return f"""
  <section class="p-section">
    <div class="p-section-head">
      <div class="p-section-num">{esc(num)}</div>
      <div>
        <div class="p-kicker">{esc(kicker)}</div>
        <h2>{esc(title)}<span class="dot">.</span></h2>
        <p class="p-section-desc">{esc(desc)}</p>
      </div>
    </div>
    {body}
  </section>
"""


def nav_html(active: str) -> str:
    pages = [
        ("focus-star.html", "The 5 Ps", active == "focus-star"),
        ("product.html", "Product", active == "product"),
        ("people.html", "People", active == "people"),
        ("purpose.html", "Purpose", active == "purpose"),
        ("promise.html", "Promise", active == "promise"),
        ("personality.html", "Personality", active == "personality"),
    ]
    links = "".join(
        f'<a href="{href}" class="{"active" if is_active else ""}">{label}</a>'
        for href, label, is_active in pages
    )
    return f"""
<aside class="sidebar">
  <div class="brand-mark">
    <div class="name">FP<span class="dot">.</span></div>
    <div class="meta">Brand OS</div>
  </div>
  <div class="nav-section">
    <div class="label">Sections</div>
    <details class="nav-group" ><summary><span class="group-letter">.</span><span class="group-label">Overview</span></summary><div class="nav-list"><a href="index.html" class="">Home</a></div></details>
    <details class="nav-group" open><summary><span class="group-letter">A</span><span class="group-label">Brand Strategy</span></summary><div class="nav-list">{links}</div></details>
    <details class="nav-group" ><summary><span class="group-letter">B</span><span class="group-label">Brand Identity</span></summary><div class="nav-list"><a href="creative-direction.html" class="">Creative Direction</a><a href="visual.html" class="">Look &amp; Feel</a><a href="voice.html" class="">Voice</a><a href="signature.html" class="">Signature</a></div></details>
    <details class="nav-group" ><summary><span class="group-letter">C</span><span class="group-label">Application</span></summary><div class="nav-list"><a href="application.html" class="">Overview</a><a href="application-copy.html" class="">Copy</a><a href="application-email.html" class="">Email</a><a href="application-social.html" class="">Social</a><a href="application-proof.html" class="">Proof</a><a href="application-assets.html" class="">Assets</a><a href="application-web.html" class="">Website</a><a href="application-stationery.html" class="">Stationery</a></div></details>
    <details class="nav-group" ><summary><span class="group-letter">D</span><span class="group-label">Personal Branding</span></summary><div class="nav-list"><a href="founder-identity.html" class="">Founder Identity</a><a href="background.html" class="">Background</a><a href="imagery.html" class="">Imagery</a></div></details>
  </div>
  <div class="toolbar-mini">
    <div class="row"><span>Section</span><strong>Strategy</strong></div>
    <div class="row"><span>Use</span><strong>AI + creative</strong></div>
    <div class="row"><span>Center</span><strong>Curiosity</strong></div>
  </div>
</aside>
"""


def hero(pillar: dict[str, Any], image: dict[str, Any] | None, tags: list[str]) -> str:
    case = pillar["case"]
    contract = case["contract"]
    desc = strip_tags(case.get("desc", contract["core_decision"]))
    image_path = (image or {}).get("path", "assets/moodboard/quality-workspace.jpg")
    image_alt = (image or {}).get("alt", f"{pillar['title']} image direction.")
    tag_html = "".join(f"<span>{esc(tag)}</span>" for tag in tags[:5])
    return f"""
  <section class="p-hero">
    <div class="p-hero-copy">
      <div class="p-kicker">Section A · {esc(pillar["code"])} · Brand Strategy</div>
      <h1>{esc(pillar["title"])}<span class="dot">.</span></h1>
      <p>{esc(desc)}</p>
      <div class="p-tags">{tag_html}</div>
    </div>
    <figure class="p-hero-media">
      <img src="{esc(image_path)}" alt="{esc(image_alt)}">
      <figcaption class="p-caption">Image direction: {esc(contract["output_controls"].get("image", ""))}</figcaption>
    </figure>
  </section>
  <div class="p-thesis">{esc((case.get("intelligence") or {}).get("thesis", contract["page_thesis"]))}</div>
"""


def product_sections(pillar: dict[str, Any]) -> str:
    case = pillar["case"]
    contract = case["contract"]
    intel = case.get("intelligence") or {}
    return "".join(
        [
            section(
                "01",
                "Strategic decision",
                "What is being sold",
                "Product defines the offer logic: what the client buys, what it replaces, and what AI must protect.",
                f"""
                <div class="p-grid">
                  {card(pillar["case"].get("title", "Brand Therapy"), "Offer name", intel.get("offer_definition", contract["core_decision"]), True)}
                  {card("Clarity that holds", "Client outcome", "The client stops tweaking from taste, anxiety, or imitation. Decisions get a reason.")}
                  {card("Strategic diagnosis", "Offer category", contract["plain_meaning"])}
                </div>
                """,
            ),
            section(
                "02",
                "Value stack",
                "What clients buy",
                "Every Product output should show why the process matters before listing deliverables.",
                f"""<div class="p-row-list">
                  {''.join(row(item.split(':', 1)[0], item.split(':', 1)[1].strip() if ':' in item else item) for item in intel.get("value_stack", []))}
                  {row("Real test", "If the work cannot help a client make a sharper decision after the session, it is decoration, not Brand Therapy.")}
                </div>""",
            ),
            section(
                "03",
                "Offer boundaries",
                "What belongs and what does not",
                "These filters prevent the offer from drifting into agency, therapy, coaching, or template language.",
                f"""<div class="p-grid two">
                  {card("Belongs", "Rules in", contract["rules_in"])}
                  {card("Does not belong", "Rules out", contract["rules_out"], True)}
                </div>""",
            ),
            marketing_and_controls(pillar, intel.get("buying_triggers", [])),
        ]
    )


def people_sections(pillar: dict[str, Any]) -> str:
    case = pillar["case"]
    contract = case["contract"]
    persona = case.get("persona") or {}
    details = case.get("details") or {}
    return "".join(
        [
            section(
                "01",
                "Audience decision",
                "Who this is really for",
                "People is the highest-risk test. AI must understand the person, not just the segment label.",
                f"""<div class="p-grid">
                  {card("Wrong comparison", "Strategic choice", contract["core_decision"], True)}
                  {card("Inner line", "Persona quote", persona.get("quote", "The work is not generic. The way it is explained is."))}
                  {card("What changes", "Business outcome", persona.get("need", contract["page_thesis"]))}
                </div>""",
            ),
            section(
                "02",
                "Persona",
                "The Invisible Expert",
                "The audience is defined by the market reading the work too flatly, not by a founder label.",
                f"""<div class="p-grid two">
                  {card(persona.get("role", "The Invisible Expert"), "Primary persona", [persona.get("context", ""), persona.get("need", "")], True)}
                  <article class="p-card">
                    <div class="p-card-label">Persona image</div>
                    <img class="p-inline-image" src="{esc((persona.get("image") or {}).get("path", "assets/people/persona-invisible-expert-female.png"))}" alt="{esc((persona.get("image") or {}).get("alt", "Persona image."))}">
                    <p>{esc(contract["output_controls"].get("image", ""))}</p>
                  </article>
                </div>""",
            ),
            section(
                "03",
                "Psychographics",
                "What they care about",
                "These fields drive better copy, imagery, offer framing, proof, and page structure.",
                f"""<div class="p-grid">
                  {card("Values", "Psychographics", persona.get("psychographics", details.get("Psychographics", [])))}
                  {card("Needs", "Functional", persona.get("needs", details.get("Needs and wants", [])))}
                  {card("Wants", "Business", persona.get("wants", []), True)}
                </div>""",
            ),
            section(
                "04",
                "Marketing use",
                "Triggers, criteria, and objections",
                "This is the part that should inform landing pages, sales calls, content, email, proof, and offer framing.",
                f"""<div class="p-grid">
                  {card("When they buy", "Decision triggers", details.get("Decision triggers", [persona.get("decisionTrigger", "")]))}
                  {card("What must be true", "Buying criteria", persona.get("buyingCriteria", []))}
                  {card("What blocks them", "Objections", persona.get("objections", []), True)}
                </div>""",
            ),
            section(
                "05",
                "Creative controls",
                "How to show this audience",
                "The image system should communicate competence and specific thought, not broken-beginner transformation.",
                f"""<div class="p-grid">
                  {card("Alternatives", "Competitive context", persona.get("alternatives", details.get("Alternatives", [])))}
                  {card("Image signal", "Creative direction", persona.get("creativeDirection", details.get("Creative rules", [])), True)}
                  {card("AI rule", "Generation", contract["output_controls"].get("ai", ""))}
                </div>""",
            ),
        ]
    )


def generic_sections(pillar: dict[str, Any]) -> str:
    case = pillar["case"]
    contract = case["contract"]
    intel = case.get("intelligence") or {}
    rows = []
    for key, value in intel.items():
        if key in {"thesis", "image", "minimum_fields"}:
            continue
        title = key.replace("_", " ").title()
        rows.append(row(title, value))
    return "".join(
        [
            section(
                "01",
                "Strategic decision",
                "The operating choice",
                "This is the decision this P owns. Everything downstream should preserve it.",
                f"""<div class="p-grid">
                  {card(pillar["case"].get("title", pillar["title"]), "Core decision", contract["core_decision"], True)}
                  {card("Plain meaning", "Interpretation", contract["plain_meaning"])}
                  {card("Tradeoff", "Cost of choice", contract["tradeoff"])}
                </div>""",
            ),
            section(
                "02",
                "Intelligence layer",
                "What AI must know",
                "These fields are compact enough for AI context and precise enough for design and marketing decisions.",
                f"""<div class="p-row-list">{''.join(rows)}</div>""",
            ),
            section(
                "03",
                "Rules",
                "What belongs and what does not",
                "A real strategy excludes things. These are the hard filters for copy, design, content, and sales.",
                f"""<div class="p-grid two">
                  {card("Belongs", "Rules in", contract["rules_in"])}
                  {card("Does not belong", "Rules out", contract["rules_out"], True)}
                </div>""",
            ),
            marketing_and_controls(pillar, intel.get("content_prompts", intel.get("story_prompts", []))),
        ]
    )


def marketing_and_controls(pillar: dict[str, Any], triggers: list[str]) -> str:
    contract = pillar["case"]["contract"]
    controls = contract["output_controls"]
    body = f"""<div class="p-grid">
      {card("When it matters", "Triggers", triggers or [contract["page_thesis"]])}
      {card("Show evidence", "Proof required", contract["proof_required"])}
      {card("AI behavior", "AI rule", controls.get("ai", ""), True)}
    </div>
    <div class="p-grid">
      {card("Copy", "Output control", controls.get("copy", ""))}
      {card("Visual", "Output control", controls.get("visual", ""))}
      {card("Image", "Output control", controls.get("image", ""))}
    </div>"""
    return section(
        "04",
        "Marketing use",
        "Triggers, proof, and output controls",
        "This is the AI-readable layer for website copy, landing pages, sales, content, visual direction, and image prompts.",
        body,
    )


def page_tags(pillar: dict[str, Any]) -> list[str]:
    case = pillar["case"]
    persona = case.get("persona") or {}
    if persona.get("tags"):
        return persona["tags"]
    intel = case.get("intelligence") or {}
    if pillar["id"] == "product":
        return ["Brand Therapy", "Clarity", "Decision system", "Working blueprint"]
    if pillar["id"] == "purpose":
        return ["Specificity", "Selection", "Less interchangeable", "Useful distinction"]
    if pillar["id"] == "promise":
        return ["Curiosity", "Diagnosis", "Questions first", "Sharper choices"]
    if pillar["id"] == "personality":
        return ["Dry diagnosis", "Archetypes", "Observed tension", "Sparse humor"]
    return [pillar["title"], *(intel.get("minimum_fields") or [])[:3]]


def image_for(pillar: dict[str, Any]) -> dict[str, Any] | None:
    case = pillar["case"]
    if case.get("persona", {}).get("image"):
        return case["persona"]["image"]
    return (case.get("intelligence") or {}).get("image")


def build_page(source: dict[str, Any], pillar: dict[str, Any]) -> str:
    page_id = pillar["id"]
    if page_id == "product":
        body = product_sections(pillar)
    elif page_id == "people":
        body = people_sections(pillar)
    else:
        body = generic_sections(pillar)
    next_page = {
        "product": ("people.html", "People"),
        "people": ("purpose.html", "Purpose"),
        "purpose": ("promise.html", "Promise"),
        "promise": ("personality.html", "Personality"),
        "personality": ("focus-star.html", "Focus Star"),
    }[page_id]
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(pillar["title"])} · FP Brand OS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{esc(source["visual"]["fonts"]["googleFontsUrl"])}" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body class="grain">
<div class="shell">
{nav_html(page_id)}
<main class="content">
{hero(pillar, image_for(pillar), page_tags(pillar))}
{body}
  <div class="footer-nav">
    <span>Section A · {esc(pillar["title"])} intelligence</span>
    <span><a href="{esc(next_page[0])}">{esc(next_page[1])} &rarr;</a></span>
  </div>
</main>
</div>
</body>
</html>
"""
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def build_focus_star_page(source: dict[str, Any]) -> str:
    decision_cards = []
    for pillar in source["pillars"]:
        contract = pillar["case"]["contract"]
        decision_cards.append(
            f"""
      <article class="p-card">
        <div class="p-card-label">{esc(pillar["code"])} · {esc(pillar["title"])}</div>
        <h3>{esc(pillar["case"].get("title", pillar["title"]))}</h3>
        <p>{esc(contract["core_decision"])}</p>
        <a href="{esc(pillar["id"])}.html">Open {esc(pillar["title"])}</a>
      </article>
            """
        )
    website_rules = compact_ai_context(source)["website_generation_rules"]
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Focus Star · FP Brand OS</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{esc(source["visual"]["fonts"]["googleFontsUrl"])}" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body class="grain">
<div class="shell">
{nav_html("focus-star")}
<main class="content">
  <section class="p-hero">
    <div class="p-hero-copy">
      <div class="p-kicker">Section A · Focus Star · Brand Strategy</div>
      <h1>Focus Star<span class="dot">.</span></h1>
      <p>{esc(source["brand"]["description"])}</p>
      <div class="p-tags">
        <span>Product</span><span>People</span><span>Purpose</span><span>Promise</span><span>Personality</span>
      </div>
    </div>
    <figure class="p-hero-media">
      <img src="assets/generated/signature-viewfinder-hero.png" alt="FP viewfinder visual direction.">
      <figcaption class="p-caption">Center: {esc(source["center"])}. Section A sets the strategic standard for copy, design, offers, proof, and AI-generated work.</figcaption>
    </figure>
  </section>
  <div class="p-thesis">{esc(source["brand"]["description"])}</div>

  {section(
      "01",
      "Interactive compass",
      "The Focus Star in motion",
      "A usable compass for checking whether future copy, design, offers, proof, and content still point to the same strategy.",
      '<iframe src="assets/focus-star/index.html" title="Generated Focus Star Compass" class="compass-embed"></iframe>',
  )}

  {section(
      "02",
      "Strategy spine",
      "The five decisions",
      "These are not website paragraphs. They are the strategy contract used by AI, design, marketing, sales, and creative direction.",
      f'<div class="p-grid">{"".join(decision_cards)}</div>',
  )}

  {section(
      "03",
      "AI application rules",
      "How this should shape output",
      "Use these rules before generating websites, landing pages, email, social, proof, or image prompts.",
      f'<div class="p-grid">{card("One-shot website test", "AI guidance", website_rules, True)}{card("Quality check", "Use", ["The audience tension should be clear before the hero gets polished.", "The offer should create clarity, confidence, and sharper decisions.", "The voice should feel spoken, exact, and slightly dry."])}</div>',
  )}

  <div class="footer-nav">
    <span>Section A · Focus Star</span>
    <span><a href="product.html">Product &rarr;</a></span>
  </div>
</main>
</div>
</body>
</html>
"""
    return "\n".join(line.rstrip() for line in html.splitlines()) + "\n"


def compact_ai_context(source: dict[str, Any]) -> dict[str, Any]:
    pages: dict[str, Any] = {}
    for pillar in source["pillars"]:
        case = pillar["case"]
        contract = case["contract"]
        pages[pillar["id"]] = {
            "code": pillar["code"],
            "title": pillar["title"],
            "label": pillar["title"],
            "strategic_question": contract["strategic_question"],
            "core_decision": contract["core_decision"],
            "plain_meaning": contract["plain_meaning"],
            "page_thesis": contract["page_thesis"],
            "rules_in": contract["rules_in"],
            "rules_out": contract["rules_out"],
            "tradeoff": contract["tradeoff"],
            "proof_required": contract["proof_required"],
            "output_controls": contract["output_controls"],
            "intelligence": case.get("intelligence"),
            "persona": case.get("persona"),
        }
    return {
        "artifact": "section-a.ai-context",
        "schema_version": "section_a.single_source.v1",
        "generated_from": "assets/focus-star/section-a.source.json",
        "source_snapshot": source.get("source", {}).get("fetchedAt", "unknown"),
        "brand": source["brand"],
        "center": source["center"],
        "source": source.get("source", {}),
        "usage": [
            "Use this compact pack before generating websites, landing pages, email, social, proof, and image prompts.",
            "Treat approved contract fields as hard strategy.",
            "If a required field is missing, ask or mark missing. Do not invent strategy.",
            "Do not use the rendered HTML pages as source; they are generated from this pack.",
        ],
        "website_generation_rules": [
            "Start with the People tension and Product outcome before writing hero polish.",
            "Tie visibility to differentiation and better-fit demand, not attention for its own sake.",
            "Lead Product with clarity, confidence, and tangible direction before process language.",
            "Use Purpose as the selection filter: less interchangeable, easier to choose.",
            "Use Promise as the behavior rule: curiosity before certainty.",
            "Use Personality as the sentence rule: spoken, exact, slightly dry, never guru or AI thought leadership.",
        ],
        "pages": pages,
    }


def main() -> int:
    source = load_source()

    generated_config = json.loads(json.dumps(source))
    generated_config.setdefault("source", {})["generatedFrom"] = "assets/focus-star/section-a.source.json"
    generated_config["source"]["generatedBy"] = "scripts/build-section-a.py"
    write_json(CONFIG_JSON_PATH, generated_config)
    CONFIG_JS_PATH.write_text(
        "window.FOCUS_STAR_CONFIG = "
        + json.dumps(generated_config, indent=2, ensure_ascii=True)
        + ";\n"
    )
    print(f"wrote {CONFIG_JS_PATH.relative_to(ROOT)}")

    ai_context = compact_ai_context(generated_config)
    write_json(AI_CONTEXT_PATH, ai_context)

    pillars = {pillar["id"]: pillar for pillar in generated_config["pillars"]}
    focus_path = ROOT / "focus-star.html"
    focus_path.write_text(build_focus_star_page(generated_config))
    print(f"wrote {focus_path.relative_to(ROOT)}")
    for page_id in PAGE_ORDER:
        page_path = ROOT / f"{page_id}.html"
        page_path.write_text(build_page(generated_config, pillars[page_id]))
        print(f"wrote {page_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
