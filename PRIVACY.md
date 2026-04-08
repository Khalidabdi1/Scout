# Privacy Policy

Last updated: April 8, 2026

## Overview

`design-md` is a Claude Code plugin that scans files in a project and helps create a `design.md` document. This plugin is designed to operate on local project files and does not include its own telemetry, analytics, or advertising systems.

## What This Plugin Accesses

When you run `/design-md:generate`, the plugin may read files from the current project directory to understand the design system. This can include files such as:

- `package.json`
- CSS, SCSS, Less, and other style files
- Tailwind configuration and theme files
- UI component files such as `.tsx`, `.jsx`, `.vue`, or `.svelte`

The scanner is implemented in `skills/generate/scripts/scan_project.py` and uses the Python standard library only.

## What This Plugin Creates

The plugin writes a Markdown file such as `design.md`, `DESIGN.md`, or another Markdown path you choose. That generated file may include design tokens, component descriptions, and style patterns derived from your codebase.

## Data Collection

This plugin does not intentionally collect personal data.

This plugin does not include:

- analytics
- crash reporting
- usage tracking
- cookies
- background network requests owned by the plugin

## Data Sharing

This plugin does not, by itself, upload project files or scanner output to a server controlled by this repository.

However, this plugin runs inside Claude Code. Your use of Claude Code may involve sending prompts, file contents, or tool output to Anthropic or other services configured in your Claude Code environment. That processing is governed by the privacy terms and settings of Claude Code and any services you connect to it, not by this repository alone.

## Data Storage

This plugin stores data only in files you explicitly create or update while using it, such as:

- `design.md`
- `DESIGN.md`
- another Markdown output path you request

The plugin repository itself does not provide a remote database or hosted storage service.

## User Control

You control when the plugin runs and which repository it scans.

You can reduce what is processed by:

- running the plugin only in projects you choose
- reviewing the generated `design.md` before sharing it
- editing or deleting generated files at any time
- uninstalling the plugin from Claude Code when you no longer want to use it

## Security Notes

Because the plugin can summarize code and design tokens into a Markdown document, avoid running it on repositories that contain sensitive information unless you are comfortable reviewing the output carefully.

## Changes

If this plugin's behavior changes in a way that materially affects privacy, this file should be updated.

## Contact

Repository: [Khalidabdi1/Scout](https://github.com/Khalidabdi1/Scout)
