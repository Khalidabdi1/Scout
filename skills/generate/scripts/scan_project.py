#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".idea",
    ".next",
    ".nuxt",
    ".output",
    ".parcel-cache",
    ".svelte-kit",
    ".turbo",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "out",
    "storybook-static",
    "target",
    "tmp",
    "vendor",
    "venv",
}

TEXT_EXTENSIONS = {
    ".astro",
    ".css",
    ".html",
    ".js",
    ".json",
    ".jsx",
    ".less",
    ".mdx",
    ".pcss",
    ".sass",
    ".scss",
    ".svelte",
    ".styl",
    ".ts",
    ".tsx",
    ".vue",
}

SPECIAL_FILENAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
}

PRIORITY_NAMES = (
    "package.json",
    "tailwind.config.",
    "theme.",
    "tokens.",
    "globals.",
    "global.",
    "styles.",
    "app.",
    "layout.",
    "page.",
)

HEX_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FUNCTION_COLOR_RE = re.compile(r"\b(?:rgb|rgba|hsl|hsla)\([^)]*\)")
CSS_VARIABLE_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;}{]+)")
FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}{]+)")
FONT_SIZE_RE = re.compile(r"font-size\s*:\s*([^;}{]+)")
FONT_WEIGHT_RE = re.compile(r"font-weight\s*:\s*([^;}{]+)")
BORDER_RADIUS_RE = re.compile(r"border-radius\s*:\s*([^;}{]+)")
BOX_SHADOW_RE = re.compile(r"box-shadow\s*:\s*([^;}{]+)")
TAILWIND_SPACING_RE = re.compile(r"\b(?:p[trblxy]?|m[trblxy]?|gap|space-[xy])-(?:px|\d+(?:\.5)?)\b")
TAILWIND_RADIUS_RE = re.compile(r"\brounded(?:-(?:none|sm|md|lg|xl|2xl|3xl|full))?\b")
TAILWIND_SHADOW_RE = re.compile(r"\bshadow(?:-(?:sm|md|lg|xl|2xl|inner|none))?\b")
CLASSNAME_RE = re.compile(r"\bclass(?:Name)?\s*=\s*['\"]([^'\"]+)['\"]")
COMPONENT_PATH_RE = re.compile(r"(components|ui|screens|pages|views)", re.IGNORECASE)

TAILWIND_SCALE = {
    "px": "1px",
    "0": "0",
    "0.5": "0.125rem",
    "1": "0.25rem",
    "1.5": "0.375rem",
    "2": "0.5rem",
    "2.5": "0.625rem",
    "3": "0.75rem",
    "3.5": "0.875rem",
    "4": "1rem",
    "5": "1.25rem",
    "6": "1.5rem",
    "7": "1.75rem",
    "8": "2rem",
    "9": "2.25rem",
    "10": "2.5rem",
    "11": "2.75rem",
    "12": "3rem",
    "14": "3.5rem",
    "16": "4rem",
    "20": "5rem",
    "24": "6rem",
    "28": "7rem",
    "32": "8rem",
    "36": "9rem",
    "40": "10rem",
    "44": "11rem",
    "48": "12rem",
    "52": "13rem",
    "56": "14rem",
    "60": "15rem",
    "64": "16rem",
    "72": "18rem",
    "80": "20rem",
    "96": "24rem",
}

FRAMEWORK_HINTS = {
    "react": "React",
    "next": "Next.js",
    "vue": "Vue",
    "nuxt": "Nuxt",
    "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit",
    "astro": "Astro",
    "gatsby": "Gatsby",
    "@angular/core": "Angular",
    "tailwindcss": "Tailwind CSS",
    "styled-components": "styled-components",
    "@emotion/react": "Emotion",
    "@mui/material": "MUI",
    "@chakra-ui/react": "Chakra UI",
    "framer-motion": "Framer Motion",
    "motion": "Motion One",
}


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def sanitize_text(value: str) -> str:
    return normalize_space(value.strip().strip(","))


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def score_file(path: Path) -> tuple[int, int, str]:
    name = path.name.lower()
    path_text = str(path).lower()
    priority = 3
    if name == "package.json":
        priority = 0
    elif any(name.startswith(prefix) for prefix in PRIORITY_NAMES):
        priority = 1
    elif "tailwind" in path_text or "theme" in path_text or "token" in path_text:
        priority = 1
    elif COMPONENT_PATH_RE.search(path_text):
        priority = 2
    return (priority, len(path.parts), path_text)


def should_scan(path: Path) -> bool:
    if path.name in SPECIAL_FILENAMES:
        return True
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    name = path.name.lower()
    return any(token in name for token in ("tailwind.config", "postcss.config", "theme", "token"))


def iter_candidate_files(root: Path, max_files: int) -> list[Path]:
    candidates: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            dirname
            for dirname in dirnames
            if dirname not in IGNORE_DIRS and not dirname.startswith(".cache")
        ]
        for filename in filenames:
            path = Path(current_root, filename)
            if path.stat().st_size > 500_000:
                continue
            if should_scan(path):
                candidates.append(path)
    candidates.sort(key=score_file)
    return candidates[:max_files]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def update_bucket(
    bucket: dict[str, dict[str, object]],
    key: str,
    path: Path,
    relative: str,
    limit: int = 5,
) -> None:
    entry = bucket.setdefault(key, {"count": 0, "files": []})
    entry["count"] = int(entry["count"]) + 1
    files = entry["files"]
    if relative not in files and len(files) < limit:
        files.append(relative)


def extract_tailwind_classes(text: str) -> list[str]:
    classes: list[str] = []
    for match in CLASSNAME_RE.findall(text):
        classes.extend(token for token in match.split() if token)
    return classes


def detect_frameworks(package_json: dict[str, object]) -> list[str]:
    dependency_blocks = []
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package_json.get(key)
        if isinstance(value, dict):
            dependency_blocks.append(value)
    found = set()
    for block in dependency_blocks:
        for dependency in block:
            label = FRAMEWORK_HINTS.get(dependency)
            if label:
                found.add(label)
    return sorted(found)


def summarize_bucket(bucket: dict[str, dict[str, object]], limit: int = 8) -> list[dict[str, object]]:
    entries = []
    for value, meta in bucket.items():
        entries.append(
            {
                "value": value,
                "count": int(meta["count"]),
                "files": sorted(meta["files"]),
            }
        )
    entries.sort(key=lambda item: (-int(item["count"]), str(item["value"])))
    return entries[:limit]


def extract_component_name(path: Path) -> str | None:
    if path.suffix.lower() not in {".tsx", ".jsx", ".vue", ".svelte"}:
        return None
    stem = path.stem
    if not stem or stem[0].islower():
        return None
    if stem in {"App", "Page", "Layout"} and not COMPONENT_PATH_RE.search(str(path)):
        return None
    return stem


def scan_project(root: Path, max_files: int) -> dict[str, object]:
    package_json: dict[str, object] = {}
    package_path = root / "package.json"
    if package_path.exists():
        try:
            package_json = json.loads(read_text(package_path))
        except json.JSONDecodeError:
            package_json = {}

    files = iter_candidate_files(root, max_files)
    color_values: dict[str, dict[str, object]] = {}
    color_variables: dict[str, dict[str, object]] = {}
    font_families: dict[str, dict[str, object]] = {}
    font_sizes: dict[str, dict[str, object]] = {}
    font_weights: dict[str, dict[str, object]] = {}
    spacing_tokens: dict[str, dict[str, object]] = {}
    radius_values: dict[str, dict[str, object]] = {}
    shadow_values: dict[str, dict[str, object]] = {}
    tailwind_spacing: dict[str, dict[str, object]] = {}
    tailwind_radius: dict[str, dict[str, object]] = {}
    tailwind_shadow: dict[str, dict[str, object]] = {}
    notable_files: list[str] = []
    components: Counter[str] = Counter()
    color_mode_markers: set[str] = set()

    for path in files:
        relative = relpath(path, root)
        if len(notable_files) < 15 and score_file(path)[0] <= 2:
            notable_files.append(relative)

        text = read_text(path)
        lowered = text.lower()

        if "prefers-color-scheme" in lowered or "dark:" in lowered or "data-theme" in lowered:
            color_mode_markers.add("dark-mode-support")

        for value in HEX_COLOR_RE.findall(text):
            update_bucket(color_values, value, path, relative)
        for value in FUNCTION_COLOR_RE.findall(text):
            update_bucket(color_values, sanitize_text(value), path, relative)

        for name, raw_value in CSS_VARIABLE_RE.findall(text):
            value = sanitize_text(raw_value)
            if "color" in name:
                update_bucket(color_variables, f"{name}: {value}", path, relative)
            elif any(token in name for token in ("font",)):
                update_bucket(font_families, f"{name}: {value}", path, relative)
            elif any(token in name for token in ("space", "gap", "padding", "margin", "gutter")):
                update_bucket(spacing_tokens, f"{name}: {value}", path, relative)
            elif "radius" in name:
                update_bucket(radius_values, f"{name}: {value}", path, relative)
            elif "shadow" in name:
                update_bucket(shadow_values, f"{name}: {value}", path, relative)

        for value in FONT_FAMILY_RE.findall(text):
            update_bucket(font_families, sanitize_text(value), path, relative)
        for value in FONT_SIZE_RE.findall(text):
            update_bucket(font_sizes, sanitize_text(value), path, relative)
        for value in FONT_WEIGHT_RE.findall(text):
            update_bucket(font_weights, sanitize_text(value), path, relative)
        for value in BORDER_RADIUS_RE.findall(text):
            update_bucket(radius_values, sanitize_text(value), path, relative)
        for value in BOX_SHADOW_RE.findall(text):
            update_bucket(shadow_values, sanitize_text(value), path, relative)

        for token in TAILWIND_SPACING_RE.findall(text):
            scale = token.rsplit("-", 1)[-1]
            exact = TAILWIND_SCALE.get(scale)
            label = f"{token} ({exact})" if exact else token
            update_bucket(tailwind_spacing, label, path, relative)
        for token in TAILWIND_RADIUS_RE.findall(text):
            update_bucket(tailwind_radius, token, path, relative)
        for token in TAILWIND_SHADOW_RE.findall(text):
            update_bucket(tailwind_shadow, token, path, relative)

        component_name = extract_component_name(path)
        if component_name:
            components[component_name] += 1

    existing_design_docs = [
        relpath(path, root)
        for path in (root / "design.md", root / "DESIGN.md")
        if path.exists()
    ]

    frameworks = detect_frameworks(package_json)
    if color_mode_markers:
        frameworks.append("Dark mode patterns")

    scripts = package_json.get("scripts", {}) if isinstance(package_json.get("scripts"), dict) else {}

    return {
        "project_root": str(root),
        "package_name": package_json.get("name"),
        "frameworks": sorted(set(frameworks)),
        "scripts": sorted(scripts.keys())[:12],
        "files_scanned": len(files),
        "notable_files": notable_files,
        "existing_design_docs": existing_design_docs,
        "colors": summarize_bucket(color_values),
        "color_variables": summarize_bucket(color_variables),
        "font_families": summarize_bucket(font_families),
        "font_sizes": summarize_bucket(font_sizes),
        "font_weights": summarize_bucket(font_weights),
        "spacing_tokens": summarize_bucket(spacing_tokens),
        "tailwind_spacing": summarize_bucket(tailwind_spacing),
        "radius_values": summarize_bucket(radius_values),
        "tailwind_radius": summarize_bucket(tailwind_radius),
        "shadow_values": summarize_bucket(shadow_values),
        "tailwind_shadow": summarize_bucket(tailwind_shadow),
        "components": [
            {"name": name, "count": count}
            for name, count in components.most_common(12)
        ],
    }


def render_entries(entries: Iterable[dict[str, object]], fallback: str, limit: int = 6) -> list[str]:
    lines = []
    for item in list(entries)[:limit]:
        value = item["value"]
        count = item["count"]
        files = ", ".join(item["files"])
        lines.append(f"- `{value}` ({count} hits; {files})")
    return lines or [f"- {fallback}"]


def render_components(entries: list[dict[str, object]]) -> list[str]:
    if not entries:
        return ["- No obvious shared UI component files detected."]
    return [f"- `{item['name']}` ({item['count']} file hit(s))" for item in entries]


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Project Scan Summary",
        "",
        f"- Root: `{summary['project_root']}`",
        f"- Files scanned: `{summary['files_scanned']}`",
    ]

    package_name = summary.get("package_name")
    if package_name:
        lines.append(f"- Package name: `{package_name}`")

    frameworks = summary.get("frameworks") or []
    lines.append(
        "- Detected stack: "
        + (", ".join(f"`{framework}`" for framework in frameworks) if frameworks else "No strong framework signal detected.")
    )

    scripts = summary.get("scripts") or []
    if scripts:
        lines.append("- Package scripts: " + ", ".join(f"`{script}`" for script in scripts))

    design_docs = summary.get("existing_design_docs") or []
    if design_docs:
        lines.append("- Existing design docs: " + ", ".join(f"`{path}`" for path in design_docs))
    else:
        lines.append("- Existing design docs: none")

    lines.extend(
        [
            "",
            "## Notable Files",
            *(
                [f"- `{path}`" for path in summary.get("notable_files", [])[:12]]
                or ["- No notable design-related files detected."]
            ),
            "",
            "## Color Signals",
            "### CSS variables and named tokens",
            *render_entries(summary.get("color_variables", []), "No color variables found."),
            "",
            "### Raw color values",
            *render_entries(summary.get("colors", []), "No raw color values found."),
            "",
            "## Typography Signals",
            "### Font families",
            *render_entries(summary.get("font_families", []), "No font-family declarations found."),
            "",
            "### Font sizes",
            *render_entries(summary.get("font_sizes", []), "No explicit font-size values found."),
            "",
            "### Font weights",
            *render_entries(summary.get("font_weights", []), "No explicit font-weight values found."),
            "",
            "## Spacing and Layout Signals",
            "### CSS spacing tokens",
            *render_entries(summary.get("spacing_tokens", []), "No spacing tokens found."),
            "",
            "### Tailwind spacing utilities",
            *render_entries(summary.get("tailwind_spacing", []), "No Tailwind spacing utilities found."),
            "",
            "## Shape and Elevation Signals",
            "### Radius values",
            *render_entries(summary.get("radius_values", []), "No border-radius values found."),
            "",
            "### Tailwind radius utilities",
            *render_entries(summary.get("tailwind_radius", []), "No Tailwind radius utilities found."),
            "",
            "### Shadow values",
            *render_entries(summary.get("shadow_values", []), "No box-shadow values found."),
            "",
            "### Tailwind shadow utilities",
            *render_entries(summary.get("tailwind_shadow", []), "No Tailwind shadow utilities found."),
            "",
            "## Component Signals",
            *render_components(summary.get("components", [])),
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a project for design-system signals.")
    parser.add_argument("--project-root", default=".", help="Project root to scan.")
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=200,
        help="Maximum number of files to scan.",
    )
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    summary = scan_project(root, max_files=args.max_files)
    if args.format == "json":
        print(json.dumps(summary, indent=2))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
