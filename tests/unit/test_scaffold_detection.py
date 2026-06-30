from git_ai.services.scaffold_detection import ScaffoldDetectionService


class DiffStub:
    def __init__(self, text: str) -> None:
        self.text = text


class PromptRequestStub:
    def __init__(self, diff_text: str, language: str = "fr") -> None:
        self.diff = DiffStub(diff_text)
        self.language = language


def test_detects_nextjs_scaffold():
    diff_text = """
diff --git a/package.json b/package.json
new file mode 100644
--- /dev/null
+++ b/package.json
diff --git a/next.config.js b/next.config.js
new file mode 100644
--- /dev/null
+++ b/next.config.js
diff --git a/app/page.tsx b/app/page.tsx
new file mode 100644
--- /dev/null
+++ b/app/page.tsx
diff --git a/app/layout.tsx b/app/layout.tsx
new file mode 100644
--- /dev/null
+++ b/app/layout.tsx
diff --git a/public/logo.svg b/public/logo.svg
new file mode 100644
--- /dev/null
+++ b/public/logo.svg
diff --git a/tsconfig.json b/tsconfig.json
new file mode 100644
--- /dev/null
+++ b/tsconfig.json
diff --git a/eslint.config.mjs b/eslint.config.mjs
new file mode 100644
--- /dev/null
+++ b/eslint.config.mjs
diff --git a/README.md b/README.md
new file mode 100644
--- /dev/null
+++ b/README.md
"""

    service = ScaffoldDetectionService()
    fallback = service.detect(PromptRequestStub(diff_text))

    assert fallback is not None
    assert fallback.commit_text in {
        "chore: initialiser le projet",
        "chore: ajouter le scaffold initial Next.js",
    }


def test_detects_python_scaffold():
    diff_text = """
diff --git a/pyproject.toml b/pyproject.toml
new file mode 100644
--- /dev/null
+++ b/pyproject.toml
diff --git a/src/git_ai/__init__.py b/src/git_ai/__init__.py
new file mode 100644
--- /dev/null
+++ b/src/git_ai/__init__.py
diff --git a/src/git_ai/cli.py b/src/git_ai/cli.py
new file mode 100644
--- /dev/null
+++ b/src/git_ai/cli.py
diff --git a/tests/unit/test_cli.py b/tests/unit/test_cli.py
new file mode 100644
--- /dev/null
+++ b/tests/unit/test_cli.py
diff --git a/README.md b/README.md
new file mode 100644
--- /dev/null
+++ b/README.md
diff --git a/.gitignore b/.gitignore
new file mode 100644
--- /dev/null
+++ b/.gitignore
diff --git a/.env.example b/.env.example
new file mode 100644
--- /dev/null
+++ b/.env.example
diff --git a/git-ai.yaml.example b/git-ai.yaml.example
new file mode 100644
--- /dev/null
+++ b/git-ai.yaml.example
"""

    service = ScaffoldDetectionService()
    fallback = service.detect(PromptRequestStub(diff_text))

    assert fallback is not None
    assert fallback.commit_text.startswith("chore:")


def test_ignores_ide_noise_only():
    diff_text = """
diff --git a/.idea/workspace.xml b/.idea/workspace.xml
new file mode 100644
--- /dev/null
+++ b/.idea/workspace.xml
diff --git a/.vscode/settings.json b/.vscode/settings.json
new file mode 100644
--- /dev/null
+++ b/.vscode/settings.json
"""

    service = ScaffoldDetectionService()
    fallback = service.detect(PromptRequestStub(diff_text))

    assert fallback is None


def test_returns_none_for_regular_small_commit():
    diff_text = """
diff --git a/src/git_ai/services/commit_message_service.py b/src/git_ai/services/commit_message_service.py
index 1111111..2222222 100644
--- a/src/git_ai/services/commit_message_service.py
+++ b/src/git_ai/services/commit_message_service.py
@@ -1,3 +1,4 @@
"""

    service = ScaffoldDetectionService()
    fallback = service.detect(PromptRequestStub(diff_text))

    assert fallback is None

def test_extract_changed_files_detects_all_new_files():
    diff_text = """
diff --git a/package.json b/package.json
new file mode 100644
--- /dev/null
+++ b/package.json
diff --git a/app/page.tsx b/app/page.tsx
new file mode 100644
--- /dev/null
+++ b/app/page.tsx
"""
    service = ScaffoldDetectionService()
    files = service._extract_changed_files(diff_text)

    assert ("A", "package.json") in files
    assert ("A", "app/page.tsx") in files
    assert len(files) == 2