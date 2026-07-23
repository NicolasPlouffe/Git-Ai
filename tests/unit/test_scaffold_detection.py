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


def test_detects_dual_scaffold_and_returns_dual_message():
    diff_text = """
diff --git a/cpp-api/CMakeLists.txt b/cpp-api/CMakeLists.txt
new file mode 100644
--- /dev/null
+++ b/cpp-api/CMakeLists.txt
diff --git a/cpp-api/main.cpp b/cpp-api/main.cpp
new file mode 100644
--- /dev/null
+++ b/cpp-api/main.cpp
diff --git a/csharp-api/app.sln b/csharp-api/app.sln
new file mode 100644
--- /dev/null
+++ b/csharp-api/app.sln
diff --git a/csharp-api/src/app.csproj b/csharp-api/src/app.csproj
new file mode 100644
--- /dev/null
+++ b/csharp-api/src/app.csproj
diff --git a/csharp-api/global.json b/csharp-api/global.json
new file mode 100644
--- /dev/null
+++ b/csharp-api/global.json
diff --git a/csharp-api/Program.cs b/csharp-api/Program.cs
new file mode 100644
--- /dev/null
+++ b/csharp-api/Program.cs
diff --git a/README.md b/README.md
new file mode 100644
--- /dev/null
+++ b/README.md
diff --git a/.gitignore b/.gitignore
new file mode 100644
--- /dev/null
+++ b/.gitignore
"""

    service = ScaffoldDetectionService()
    fallback = service.detect(PromptRequestStub(diff_text, language="en"))

    assert fallback is not None
    assert fallback.commit_text == "chore: initialize C++ and C#/.NET projects"
    assert set(fallback.matched_keys) == {"cpp", "dotnet"}


def test_detects_three_scaffolds_and_returns_generic_multi_message():
    diff_text = """
diff --git a/cpp-api/CMakeLists.txt b/cpp-api/CMakeLists.txt
new file mode 100644
--- /dev/null
+++ b/cpp-api/CMakeLists.txt
diff --git a/cpp-api/main.cpp b/cpp-api/main.cpp
new file mode 100644
--- /dev/null
+++ b/cpp-api/main.cpp
diff --git a/python-api/pyproject.toml b/python-api/pyproject.toml
new file mode 100644
--- /dev/null
+++ b/python-api/pyproject.toml
diff --git a/python-api/src/app/__init__.py b/python-api/src/app/__init__.py
new file mode 100644
--- /dev/null
+++ b/python-api/src/app/__init__.py
diff --git a/python-api/tests/test_app.py b/python-api/tests/test_app.py
new file mode 100644
--- /dev/null
+++ b/python-api/tests/test_app.py
diff --git a/csharp-api/Program.cs b/csharp-api/Program.cs
new file mode 100644
--- /dev/null
+++ b/csharp-api/Program.cs
diff --git a/csharp-api/app.sln b/csharp-api/app.sln
new file mode 100644
--- /dev/null
+++ b/csharp-api/app.sln
diff --git a/csharp-api/src/app.csproj b/csharp-api/src/app.csproj
new file mode 100644
--- /dev/null
+++ b/csharp-api/src/app.csproj
diff --git a/csharp-api/global.json b/csharp-api/global.json
new file mode 100644
--- /dev/null
+++ b/csharp-api/global.json
"""

    service = ScaffoldDetectionService()
    fallback = service.detect(PromptRequestStub(diff_text, language="en"))

    assert fallback is not None
    assert fallback.commit_text == "chore: initialize multiple project scaffolds"
    assert set(fallback.matched_keys) == {"cpp", "dotnet", "python"}


def test_keeps_single_match_behavior_for_one_detected_scaffold():
    diff_text = """
diff --git a/cpp-api/CMakeLists.txt b/cpp-api/CMakeLists.txt
new file mode 100644
--- /dev/null
+++ b/cpp-api/CMakeLists.txt
diff --git a/cpp-api/main.cpp b/cpp-api/main.cpp
new file mode 100644
--- /dev/null
+++ b/cpp-api/main.cpp
diff --git a/cpp-api/src/foo.cpp b/cpp-api/src/foo.cpp
new file mode 100644
--- /dev/null
+++ b/cpp-api/src/foo.cpp
diff --git a/cpp-api/include/foo.hpp b/cpp-api/include/foo.hpp
new file mode 100644
--- /dev/null
+++ b/cpp-api/include/foo.hpp
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
diff --git a/CMakePresets.json b/CMakePresets.json
new file mode 100644
--- /dev/null
+++ b/CMakePresets.json
"""

    service = ScaffoldDetectionService()
    fallback = service.detect(PromptRequestStub(diff_text, language="fr"))

    assert fallback is not None
    assert fallback.commit_text in {
        "chore: initialiser le projet",
        "chore: ajouter le scaffold initial C++",
    }
    assert fallback.matched_keys == ("cpp",)