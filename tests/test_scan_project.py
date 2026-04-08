from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def load_module():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "generate"
        / "scripts"
        / "scan_project.py"
    )
    spec = importlib.util.spec_from_file_location("scan_project", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ScanProjectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_scan_project_extracts_design_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "package.json").write_text(
                json.dumps(
                    {
                        "name": "sample-ui",
                        "dependencies": {
                            "react": "^19.0.0",
                            "next": "^16.0.0",
                            "tailwindcss": "^4.0.0",
                        },
                        "scripts": {"dev": "next dev", "build": "next build"},
                    }
                ),
                encoding="utf-8",
            )

            (root / "src" / "app").mkdir(parents=True)
            (root / "src" / "components").mkdir(parents=True)

            (root / "src" / "app" / "globals.css").write_text(
                """
                :root {
                  --color-primary: #1D4ED8;
                  --surface-panel: #F8FAFC;
                  --space-section: 4rem;
                  --radius-card: 20px;
                  --shadow-soft: 0 12px 30px rgba(15, 23, 42, 0.12);
                }

                body {
                  font-family: "Inter", sans-serif;
                  font-size: 16px;
                  font-weight: 400;
                }
                """,
                encoding="utf-8",
            )

            (root / "src" / "components" / "Button.tsx").write_text(
                """
                export function Button() {
                  return (
                    <button className="rounded-xl bg-blue-600 px-4 py-3 shadow-lg text-white">
                      Save
                    </button>
                  );
                }
                """,
                encoding="utf-8",
            )

            (root / "src" / "app" / "page.tsx").write_text(
                """
                export default function Page() {
                  return (
                    <main className="min-h-screen bg-slate-50 px-6 py-10 dark:bg-slate-950">
                      <section className="mx-auto max-w-5xl space-y-6">
                        <h1 className="text-4xl font-semibold tracking-tight">Dashboard</h1>
                      </section>
                    </main>
                  );
                }
                """,
                encoding="utf-8",
            )

            summary = self.module.scan_project(root, max_files=50)

            self.assertIn("React", summary["frameworks"])
            self.assertIn("Next.js", summary["frameworks"])
            self.assertIn("Tailwind CSS", summary["frameworks"])
            self.assertIn("Dark mode patterns", summary["frameworks"])

            color_variable_values = [entry["value"] for entry in summary["color_variables"]]
            self.assertTrue(any("--color-primary" in value for value in color_variable_values))

            font_values = [entry["value"] for entry in summary["font_families"]]
            self.assertTrue(any("Inter" in value for value in font_values))

            component_names = [entry["name"] for entry in summary["components"]]
            self.assertIn("Button", component_names)

            markdown = self.module.render_markdown(summary)
            self.assertIn("## Color Signals", markdown)
            self.assertIn("rounded-xl", markdown)


if __name__ == "__main__":
    unittest.main()
