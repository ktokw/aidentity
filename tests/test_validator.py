"""Unit tests for aidentity.validator internal helpers and CLI commands."""

import textwrap
import tempfile
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from aidentity.validator import (
    _detect_type,
    _has_field,
    _load_yaml,
    _required_fields,
    _validate_file,
    cli,
)


# ---------------------------------------------------------------------------
# _has_field
# ---------------------------------------------------------------------------

class TestHasField:
    def test_top_level_present(self):
        assert _has_field({"key": "value"}, "key")

    def test_top_level_missing(self):
        assert not _has_field({}, "key")

    def test_nested_present(self):
        assert _has_field({"meta": {"version": "v001"}}, "meta.version")

    def test_nested_missing_intermediate(self):
        assert not _has_field({"meta": {}}, "meta.version")

    def test_nested_missing_root(self):
        assert not _has_field({}, "meta.version")

    def test_empty_string_is_falsy(self):
        assert not _has_field({"key": ""}, "key")

    def test_none_is_falsy(self):
        assert not _has_field({"key": None}, "key")

    def test_placeholder_string_is_falsy(self):
        # schema template default "string" should not count as valid
        assert not _has_field({"key": "string"}, "key")

    def test_zero_is_truthy(self):
        # 0 is a valid value (e.g., gop_counter=0)
        assert _has_field({"gop_counter": 0}, "gop_counter")

    def test_false_is_truthy(self):
        # False is a valid boolean
        assert _has_field({"flag": False}, "flag")

    def test_three_level_deep(self):
        data = {"a": {"b": {"c": "value"}}}
        assert _has_field(data, "a.b.c")

    def test_intermediate_not_dict(self):
        assert not _has_field({"meta": "scalar"}, "meta.version")


# ---------------------------------------------------------------------------
# _detect_type
# ---------------------------------------------------------------------------

class TestDetectType:
    def _path(self, name: str) -> Path:
        return Path(name)

    def test_iframe_via_meta_schema(self):
        data = {"meta": {"schema": "aidentity-v1", "version": "v001"}}
        assert _detect_type(data, self._path("whatever.yaml")) == "iframe"

    def test_pframe_via_delta_from(self):
        data = {"delta_from": "v003", "frame": {}}
        assert _detect_type(data, self._path("whatever.yaml")) == "pframe"

    def test_bframe_via_type_predict(self):
        data = {"type": "predict", "content": "..."}
        assert _detect_type(data, self._path("whatever.yaml")) == "bframe"

    def test_bframe_via_type_note(self):
        data = {"type": "note", "content": "..."}
        assert _detect_type(data, self._path("whatever.yaml")) == "bframe"

    def test_bframe_via_type_micro_delta(self):
        data = {"type": "micro_delta", "content": "..."}
        assert _detect_type(data, self._path("whatever.yaml")) == "bframe"

    def test_somatic_via_dimensions_and_mood_schema(self):
        data = {"dimensions": {}, "mood_schema": {}}
        assert _detect_type(data, self._path("whatever.yaml")) == "somatic"

    def test_filename_fallback_iframe(self):
        assert _detect_type({}, self._path("iframe_v001.yaml")) == "iframe"

    def test_filename_fallback_pframe(self):
        assert _detect_type({}, self._path("pframe_session42.yaml")) == "pframe"

    def test_filename_fallback_bframe(self):
        assert _detect_type({}, self._path("bframe_note.yaml")) == "bframe"

    def test_filename_fallback_somatic(self):
        assert _detect_type({}, self._path("somatic_v3.yaml")) == "somatic"

    def test_unknown_returns_none(self):
        assert _detect_type({}, self._path("mystery.yaml")) is None

    def test_meta_without_schema_not_iframe(self):
        # meta present but no schema key → not detected as iframe via meta path
        data = {"meta": {"version": "v001"}}
        # filename has no type hint → None
        assert _detect_type(data, self._path("thing.yaml")) is None


# ---------------------------------------------------------------------------
# _required_fields
# ---------------------------------------------------------------------------

class TestRequiredFields:
    def test_iframe_fields(self):
        fields = _required_fields("iframe")
        assert "meta.version" in fields
        assert "meta.schema" in fields
        assert "frame.event" in fields
        assert "frame.insight" in fields
        assert "frame.feeling" in fields

    def test_pframe_fields(self):
        fields = _required_fields("pframe")
        assert "delta_from" in fields
        assert "frame.event" in fields

    def test_bframe_fields(self):
        fields = _required_fields("bframe")
        assert "type" in fields
        assert "content" in fields

    def test_somatic_fields(self):
        fields = _required_fields("somatic")
        assert "dimensions" in fields
        assert "mood_schema" in fields

    def test_unknown_type_returns_empty(self):
        assert _required_fields("unknown") == []


# ---------------------------------------------------------------------------
# _validate_file
# ---------------------------------------------------------------------------

def _write_tmp(content: dict) -> Path:
    f = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w", encoding="utf-8")
    yaml.dump(content, f)
    f.close()
    return Path(f.name)


def _write_tmp_named(name: str, content: dict) -> Path:
    d = Path(tempfile.mkdtemp())
    p = d / name
    p.write_text(yaml.dump(content), encoding="utf-8")
    return p


class TestValidateFile:
    def test_valid_iframe(self):
        data = {
            "meta": {"version": "v001", "schema": "aidentity-v1"},
            "frame": {"event": "something", "insight": "learned", "feeling": "calm"},
        }
        p = _write_tmp(data)
        result = _validate_file(p)
        assert result["ok"] is True

    def test_invalid_iframe_missing_feeling(self):
        data = {
            "meta": {"version": "v001", "schema": "aidentity-v1"},
            "frame": {"event": "something", "insight": "learned"},
        }
        p = _write_tmp(data)
        result = _validate_file(p)
        assert result["ok"] is False
        assert "frame.feeling" in result["error"]

    def test_valid_pframe(self):
        data = {
            "delta_from": "v003",
            "frame": {"event": "x", "insight": "y", "feeling": "z"},
        }
        p = _write_tmp(data)
        result = _validate_file(p)
        assert result["ok"] is True

    def test_valid_bframe(self):
        data = {"type": "predict", "content": "next session will be hard"}
        p = _write_tmp(data)
        result = _validate_file(p)
        assert result["ok"] is True

    def test_bframe_forced_influence_warning(self, tmp_path, capsys):
        # DEF-20260529-474 fix: call _validate_file directly so click.echo(err=True)
        # writes to real sys.stderr, captured by capsys. `or True` removed.
        f = tmp_path / "bframe_warn.yaml"
        f.write_text(
            "type: note\ncontent: some content\nwarning:\n  forced_influence: true\n",
            encoding="utf-8",
        )
        result = _validate_file(f)
        assert result["ok"] is True
        captured = capsys.readouterr()
        assert "forced_influence" in captured.err

    def test_bframe_no_forced_influence_no_warning(self, capsys):
        data = {"type": "predict", "content": "ok"}
        p = _write_tmp(data)
        result = _validate_file(p)
        assert result["ok"] is True

    def test_valid_somatic(self):
        data = {"dimensions": {"stress": 0.3}, "mood_schema": {"PAD": {}}}
        p = _write_tmp(data)
        result = _validate_file(p)
        assert result["ok"] is True

    def test_unknown_type_from_filename(self):
        data = {}
        p = _write_tmp_named("mystery_file.yaml", data)
        result = _validate_file(p)
        assert result["ok"] is False
        assert "Cannot detect frame type" in result["error"]

    def test_override_type(self):
        # file has no type hints, but we override
        data = {"type": "predict", "content": "something"}
        p = _write_tmp(data)
        result = _validate_file(p, override_type="bframe")
        assert result["ok"] is True

    def test_yaml_parse_error(self):
        f = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w", encoding="utf-8")
        f.write(": invalid: yaml: [unclosed")
        f.close()
        result = _validate_file(Path(f.name))
        assert result["ok"] is False
        assert "YAML parse error" in result["error"]

    def test_placeholder_string_field_invalid(self):
        # schema template default value "string" should fail validation
        data = {
            "meta": {"version": "string", "schema": "aidentity-v1"},
            "frame": {"event": "real", "insight": "real", "feeling": "real"},
        }
        p = _write_tmp(data)
        result = _validate_file(p)
        assert result["ok"] is False


# ---------------------------------------------------------------------------
# CLI integration — validate command
# ---------------------------------------------------------------------------

class TestValidateCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def _valid_iframe_yaml(self) -> str:
        return textwrap.dedent("""\
            meta:
              version: v001
              schema: aidentity-v1
            frame:
              event: something happened
              insight: learned something
              feeling: calm and focused
        """)

    def test_validate_valid_file(self, tmp_path):
        f = tmp_path / "iframe_v001.yaml"
        f.write_text(self._valid_iframe_yaml(), encoding="utf-8")
        result = self.runner.invoke(cli, ["validate", str(f)])
        assert result.exit_code == 0
        assert "1 passed" in result.output

    def test_validate_missing_field_exits_1(self, tmp_path):
        f = tmp_path / "iframe_v001.yaml"
        f.write_text("meta:\n  version: v001\n  schema: aidentity-v1\n", encoding="utf-8")
        result = self.runner.invoke(cli, ["validate", str(f)])
        assert result.exit_code == 1
        assert "0 passed, 1 failed" in result.output

    def test_validate_directory(self, tmp_path):
        for i in range(3):
            f = tmp_path / f"iframe_v00{i+1}.yaml"
            f.write_text(self._valid_iframe_yaml(), encoding="utf-8")
        result = self.runner.invoke(cli, ["validate", str(tmp_path)])
        assert result.exit_code == 0
        assert "3 passed" in result.output

    def test_validate_empty_directory_exits_1(self, tmp_path):
        result = self.runner.invoke(cli, ["validate", str(tmp_path)])
        assert result.exit_code == 1

    def test_validate_type_override(self, tmp_path):
        f = tmp_path / "thing.yaml"
        f.write_text("type: predict\ncontent: next session\n", encoding="utf-8")
        result = self.runner.invoke(cli, ["validate", "--type", "bframe", str(f)])
        assert result.exit_code == 0

    def test_version(self):
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output
