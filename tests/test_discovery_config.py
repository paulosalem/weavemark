"""Tests for the two-tier config system."""

from __future__ import annotations

import json

from weavemark.discovery.config import (
    PROJECT_CONFIG_NAME,
    WeaveMarkEnvConfig,
    _find_project_config,
    load_config,
    print_env,
)


class TestWeaveMarkEnvConfig:
    def test_defaults(self):
        c = WeaveMarkEnvConfig()
        assert c.library_dirs == []
        assert c.default_model == "gpt-5.5"

    def test_effective_library_dirs_prepends_default(self, tmp_path):
        (tmp_path / "promplets").mkdir()
        c = WeaveMarkEnvConfig()
        dirs = c.effective_library_dirs(cwd=tmp_path)
        assert dirs[0] == tmp_path / "promplets"

    def test_effective_library_dirs_no_duplicate(self, tmp_path):
        promplets = tmp_path / "promplets"
        promplets.mkdir()
        c = WeaveMarkEnvConfig(library_dirs=[promplets])
        dirs = c.effective_library_dirs(cwd=tmp_path)
        assert dirs.count(promplets) == 1

    def test_effective_library_dirs_no_default_if_missing(self, tmp_path):
        c = WeaveMarkEnvConfig()
        dirs = c.effective_library_dirs(cwd=tmp_path)
        assert len(dirs) == 0

    def test_effective_library_dirs_includes_user_root(
        self,
        tmp_path,
        monkeypatch,
    ):
        global_dir = tmp_path / ".weavemark"
        user_promplets = global_dir / "promplets"
        user_promplets.mkdir(parents=True)
        monkeypatch.setattr("weavemark.discovery.config.GLOBAL_DIR", global_dir)

        dirs = WeaveMarkEnvConfig().effective_library_dirs(cwd=tmp_path)

        assert dirs == [user_promplets]


class TestFindProjectConfig:
    def test_finds_in_cwd(self, tmp_path):
        cfg = tmp_path / PROJECT_CONFIG_NAME
        cfg.write_text("{}")
        assert _find_project_config(tmp_path) == cfg

    def test_finds_in_parent(self, tmp_path):
        cfg = tmp_path / PROJECT_CONFIG_NAME
        cfg.write_text("{}")
        child = tmp_path / "sub" / "deep"
        child.mkdir(parents=True)
        assert _find_project_config(child) == cfg

    def test_returns_none_if_missing(self, tmp_path):
        child = tmp_path / "empty"
        child.mkdir()
        assert _find_project_config(child) is None


class TestLoadConfig:
    def test_empty_returns_defaults(self, tmp_path):
        c = load_config(project_dir=tmp_path)
        assert c.default_model == "gpt-5.5"
        assert c.library_dirs == []

    def test_project_config_loads(self, tmp_path):
        specs = tmp_path / "my_specs"
        specs.mkdir()
        cfg = tmp_path / PROJECT_CONFIG_NAME
        cfg.write_text(json.dumps({
            "library_dirs": ["my_specs"],
            "default_model": "claude-3",
        }))
        c = load_config(project_dir=tmp_path)
        assert c.default_model == "claude-3"
        assert specs.resolve() in c.library_dirs
        assert c._project_path == cfg

    def test_extra_library_dirs_appended(self, tmp_path):
        extra = tmp_path / "extra_specs"
        extra.mkdir()
        c = load_config(project_dir=tmp_path, extra_library_dirs=[extra])
        assert extra.resolve() in c.library_dirs

    def test_relative_paths_resolved(self, tmp_path):
        specs = tmp_path / "rel"
        specs.mkdir()
        cfg = tmp_path / PROJECT_CONFIG_NAME
        cfg.write_text(json.dumps({"library_dirs": ["rel"]}))
        c = load_config(project_dir=tmp_path)
        assert specs.resolve() in c.library_dirs

    def test_global_config_loads(self, tmp_path, monkeypatch):
        """Test that global config is loaded when present."""
        global_dir = tmp_path / "global_home" / ".weavemark"
        global_dir.mkdir(parents=True)
        global_cfg = global_dir / "config.json"
        global_cfg.write_text(json.dumps({"default_model": "global-model"}))

        monkeypatch.setattr("weavemark.discovery.config.GLOBAL_CONFIG", global_cfg)
        monkeypatch.setattr("weavemark.discovery.config.GLOBAL_DIR", global_dir)

        c = load_config(project_dir=tmp_path)
        assert c.default_model == "global-model"
        assert c._global_path == global_cfg

    def test_project_overrides_global(self, tmp_path, monkeypatch):
        """Project config values override global ones."""
        global_dir = tmp_path / "global_home" / ".weavemark"
        global_dir.mkdir(parents=True)
        global_cfg = global_dir / "config.json"
        global_cfg.write_text(json.dumps({"default_model": "global-model"}))

        proj_cfg = tmp_path / PROJECT_CONFIG_NAME
        proj_cfg.write_text(json.dumps({"default_model": "project-model"}))

        monkeypatch.setattr("weavemark.discovery.config.GLOBAL_CONFIG", global_cfg)
        monkeypatch.setattr("weavemark.discovery.config.GLOBAL_DIR", global_dir)

        c = load_config(project_dir=tmp_path)
        assert c.default_model == "project-model"

    def test_invalid_json_ignored(self, tmp_path):
        cfg = tmp_path / PROJECT_CONFIG_NAME
        cfg.write_text("NOT VALID JSON!!!")
        c = load_config(project_dir=tmp_path)
        assert c.default_model == "gpt-5.5"  # defaults preserved


class TestPrintEnv:
    def test_includes_key_info(self, tmp_path):
        (tmp_path / "promplets").mkdir()
        c = WeaveMarkEnvConfig(default_model="test-model")
        output = print_env(c, cwd=tmp_path)
        assert "test-model" in output
        assert "promplets" in output
        assert "WeaveMark Environment" in output

    def test_shows_not_found_for_missing_config(self):
        c = WeaveMarkEnvConfig()
        output = print_env(c)
        assert "(not found)" in output
