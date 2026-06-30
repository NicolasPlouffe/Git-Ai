from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
import re


IGNORED_PATH_PATTERNS: tuple[str, ...] = (
    ".DS_Store",
    ".idea/*",
    ".pytest_cache/*",
    ".ruff_cache/*",
    ".vscode/*",
    "__pycache__/*",
    "*.pyc",
    "*.pyo",
    "*.swp",
    "*.tmp",
    "bin/*",
    "build/*",
    "coverage/*",
    "dist/*",
    "node_modules/*",
    "obj/*",
)


@dataclass(frozen=True)
class ScaffoldFallback:
    commit_text: str


@dataclass(frozen=True)
class ScaffoldRule:
    key: str
    label: str
    file_signals: tuple[str, ...] = ()
    dir_signals: tuple[str, ...] = ()
    optional_signals: tuple[str, ...] = ()
    min_confidence: float = 0.55


@dataclass(frozen=True)
class ScaffoldMatch:
    confidence: float
    key: str
    label: str
    matched_signals: tuple[str, ...]


@dataclass(frozen=True)
class ScaffoldStats:
    added_count: int
    added_ratio: float
    modified_count: int
    total_count: int


RULES: tuple[ScaffoldRule, ...] = (
    ScaffoldRule(
        key="angular",
        label="Angular",
        file_signals=("angular.json", "src/main.ts", "tsconfig.json"),
        dir_signals=("src/",),
        optional_signals=("package.json",),
        min_confidence=0.70,
    ),
    ScaffoldRule(
        key="cpp",
        label="C++",
        file_signals=("CMakeLists.txt",),
        dir_signals=("include/", "src/"),
        optional_signals=("main.cpp", "src/main.cpp"),
        min_confidence=0.60,
    ),
    ScaffoldRule(
        key="dotnet",
        label="C#/.NET",
        file_signals=("Program.cs",),
        optional_signals=("*.csproj", "*.sln", "global.json"),
        min_confidence=0.60,
    ),
    ScaffoldRule(
        key="go",
        label="Go",
        file_signals=("go.mod",),
        dir_signals=("cmd/", "internal/"),
        optional_signals=("main.go",),
        min_confidence=0.60,
    ),
    ScaffoldRule(
        key="java",
        label="Java",
        file_signals=("pom.xml",),
        dir_signals=("src/main/java/",),
        optional_signals=("build.gradle", "src/test/java/"),
        min_confidence=0.60,
    ),
    ScaffoldRule(
        key="nextjs",
        label="Next.js",
        file_signals=("package.json",),
        dir_signals=("app/", "pages/"),
        optional_signals=("next.config.js", "next.config.mjs", "next.config.ts"),
        min_confidence=0.65,
    ),
    ScaffoldRule(
        key="node",
        label="Node.js",
        file_signals=("package.json",),
        optional_signals=("package-lock.json", "pnpm-lock.yaml", "yarn.lock"),
        min_confidence=0.55,
    ),
    ScaffoldRule(
        key="python",
        label="Python",
        file_signals=("pyproject.toml",),
        dir_signals=("src/", "tests/"),
        optional_signals=("requirements.txt",),
        min_confidence=0.60,
    ),
    ScaffoldRule(
        key="react",
        label="React",
        file_signals=("index.html", "package.json"),
        dir_signals=("public/", "src/"),
        optional_signals=("src/App.jsx", "src/App.tsx", "src/main.jsx", "src/main.tsx"),
        min_confidence=0.65,
    ),
    ScaffoldRule(
        key="rust",
        label="Rust",
        file_signals=("Cargo.toml",),
        dir_signals=("src/",),
        optional_signals=("src/lib.rs", "src/main.rs"),
        min_confidence=0.65,
    ),
    ScaffoldRule(
        key="solidity",
        label="Solidity",
        dir_signals=("contracts/",),
        optional_signals=("foundry.toml", "hardhat.config.js", "hardhat.config.ts", "script/", "test/"),
        min_confidence=0.65,
    ),
    ScaffoldRule(
        key="spring_boot",
        label="Spring Boot",
        dir_signals=("src/main/java/", "src/main/resources/"),
        optional_signals=("application.properties", "application.yml", "build.gradle", "pom.xml"),
        min_confidence=0.65,
    ),
    ScaffoldRule(
        key="vite",
        label="Vite",
        file_signals=("index.html", "package.json"),
        dir_signals=("src/",),
        optional_signals=("src/main.js", "src/main.ts", "src/main.tsx", "vite.config.js", "vite.config.ts"),
        min_confidence=0.65,
    ),
)


class ScaffoldDetectionService:
    """Détecte un scaffold initial et renvoie un fallback local si le signal est assez fort."""

    def __init__(
        self,
        min_added_files: int = 8,
        min_added_ratio: float = 0.75,
        max_modified_files: int = 2,
        min_confidence: float = 0.55,
        contextualized_message_confidence: float = 0.75,
    ) -> None:
        self._contextualized_message_confidence = contextualized_message_confidence
        self._max_modified_files = max_modified_files
        self._min_added_files = min_added_files
        self._min_added_ratio = min_added_ratio
        self._min_confidence = min_confidence

    def detect(self, request) -> ScaffoldFallback | None:
        diff_text = getattr(request.diff, "text", "") or ""
        if not diff_text.strip():
            return None

        files = self._extract_changed_files(diff_text)
        if not files:
            return None

        relevant_files = [
            (change_type, path)
            for change_type, path in files
            if not self._is_ignored_path(path)
        ]
        if not relevant_files:
            return None

        stats = self._build_stats(relevant_files)
        if not self._passes_bootstrap_gate(stats):
            return None

        added_paths = [path for change_type, path in relevant_files if change_type == "A"]
        if not added_paths:
            return None

        best_match = self._find_best_match(added_paths)
        if best_match is None:
            return None

        if best_match.confidence < self._min_confidence:
            return None

        message = self._build_commit_message(
            language=getattr(request, "language", "en"),
            match=best_match,
        )
        return ScaffoldFallback(commit_text=message)

    def _build_commit_message(self, language: str, match: ScaffoldMatch) -> str:
        normalized_language = (language or "en").lower()

        if match.confidence >= self._contextualized_message_confidence:
            return self._build_contextualized_message(normalized_language, match.label)

        return self._build_generic_message(normalized_language)

    def _build_contextualized_message(self, language: str, label: str) -> str:
        messages = {
            "en": f"chore: add initial {label} scaffold",
            "es": f"chore: agregar scaffold inicial de {label}",
            "fr": f"chore: ajouter le scaffold initial {label}",
        }
        return messages.get(language, messages["en"])

    def _build_generic_message(self, language: str) -> str:
        messages = {
            "en": "chore: initialize project",
            "es": "chore: inicializar el proyecto",
            "fr": "chore: initialiser le projet",
        }
        return messages.get(language, messages["en"])

    def _build_stats(self, files: list[tuple[str, str]]) -> ScaffoldStats:
        added_count = sum(1 for change_type, _ in files if change_type == "A")
        modified_count = sum(1 for change_type, _ in files if change_type != "A")
        total_count = len(files)
        added_ratio = added_count / total_count if total_count else 0.0

        return ScaffoldStats(
            added_count=added_count,
            added_ratio=added_ratio,
            modified_count=modified_count,
            total_count=total_count,
        )

    def _extract_changed_files(self, diff_text: str) -> list[tuple[str, str]]:
        blocks = self._split_diff_blocks(diff_text)
        results: list[tuple[str, str]] = []

        for block in blocks:
            path = self._extract_path_from_block(block)
            if path is None:
                continue

            change_type = self._extract_change_type_from_block(block)
            if change_type is None:
                continue

            results.append((change_type, path))

        deduplicated: dict[str, str] = {}
        for change_type, path in results:
            deduplicated[path] = change_type

        return [(change_type, path) for path, change_type in deduplicated.items()]

    def _extract_change_type_from_block(self, block: list[str]) -> str | None:
        if any(line.startswith("new file mode ") for line in block):
            return "A"
        if any(line.startswith("--- /dev/null") for line in block):
            return "A"
        if any(line.startswith("deleted file mode ") for line in block):
            return "D"
        if any(line.startswith("+++ /dev/null") for line in block):
            return "D"
        if any(line.startswith("@@ ") for line in block):
            return "M"
        return None

    def _extract_path_from_block(self, block: list[str]) -> str | None:
        for line in block:
            if line.startswith("+++ b/"):
                return line[6:]

        for line in block:
            if line.startswith("diff --git "):
                return self._extract_path_from_diff_header(line)

        return None

    def _extract_path_from_diff_header(self, header: str) -> str | None:
        match = re.match(r"^diff --git a/(.+?) b/(.+)$", header)
        if not match:
            return None
        return match.group(2)

    def _find_best_match(self, added_paths: list[str]) -> ScaffoldMatch | None:
        candidates: list[ScaffoldMatch] = []

        for rule in RULES:
            match = self._score_rule(rule, added_paths)
            if match is not None:
                candidates.append(match)

        if not candidates:
            return None

        candidates.sort(key=lambda item: item.confidence, reverse=True)
        return candidates[0]

    def _is_ignored_path(self, path: str) -> bool:
        return any(fnmatch(path, pattern) for pattern in IGNORED_PATH_PATTERNS)

    def _match_dir_signal(self, path: str, signal: str) -> bool:
        return path.startswith(signal)

    def _match_path_signal(self, path: str, signal: str) -> bool:
        return path == signal or fnmatch(path, signal)

    def _matched_dir_signals(self, paths: list[str], signals: tuple[str, ...]) -> list[str]:
        matched: list[str] = []
        for signal in signals:
            if any(self._match_dir_signal(path, signal) for path in paths):
                matched.append(signal)
        return matched

    def _matched_path_signals(self, paths: list[str], signals: tuple[str, ...]) -> list[str]:
        matched: list[str] = []
        for signal in signals:
            if any(self._match_path_signal(path, signal) for path in paths):
                matched.append(signal)
        return matched

    def _passes_bootstrap_gate(self, stats: ScaffoldStats) -> bool:
        return (
            stats.added_count >= self._min_added_files
            and stats.added_ratio >= self._min_added_ratio
            and stats.modified_count <= self._max_modified_files
        )

    def _score_rule(self, rule: ScaffoldRule, added_paths: list[str]) -> ScaffoldMatch | None:
        file_matches = self._matched_path_signals(added_paths, rule.file_signals)
        dir_matches = self._matched_dir_signals(added_paths, rule.dir_signals)
        optional_matches = self._matched_path_signals(added_paths, rule.optional_signals)
        optional_dir_matches = self._matched_dir_signals(added_paths, rule.optional_signals)

        all_optional_matches = list(dict.fromkeys(optional_matches + optional_dir_matches))

        score = 0.0
        if rule.file_signals:
            score += min(len(file_matches) / len(rule.file_signals), 1.0) * 0.5
        if rule.dir_signals:
            score += min(len(dir_matches) / len(rule.dir_signals), 1.0) * 0.3
        if rule.optional_signals:
            score += min(len(all_optional_matches) / len(rule.optional_signals), 1.0) * 0.2

        score = min(score, 1.0)
        if score < rule.min_confidence:
            return None

        matched_signals = tuple(dict.fromkeys(file_matches + dir_matches + all_optional_matches))
        return ScaffoldMatch(
            confidence=round(score, 2),
            key=rule.key,
            label=rule.label,
            matched_signals=matched_signals,
        )

    def _split_diff_blocks(self, diff_text: str) -> list[list[str]]:
        blocks: list[list[str]] = []
        current_block: list[str] = []

        for raw_line in diff_text.splitlines():
            line = raw_line.rstrip()

            if line.startswith("diff --git "):
                if current_block:
                    blocks.append(current_block)
                current_block = [line]
                continue

            if current_block:
                current_block.append(line)

        if current_block:
            blocks.append(current_block)

        return blocks