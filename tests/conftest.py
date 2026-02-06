import shutil
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def tmp_output(tmp_path):
    return tmp_path / "output"


@pytest.fixture
def minimal_md(fixtures_dir):
    return fixtures_dir / "minimal.md"


@pytest.fixture
def code_split_md(fixtures_dir):
    return fixtures_dir / "code_split.md"


@pytest.fixture
def flow_diagram_md(fixtures_dir):
    return fixtures_dir / "flow_diagram.md"


@pytest.fixture
def table_split_md(fixtures_dir):
    return fixtures_dir / "table_split.md"


@pytest.fixture
def callout_boxes_md(fixtures_dir):
    return fixtures_dir / "callout_boxes.md"


@pytest.fixture
def math_md(fixtures_dir):
    return fixtures_dir / "math.md"


@pytest.fixture
def arrows_md(fixtures_dir):
    return fixtures_dir / "arrows.md"


@pytest.fixture
def manim_simple_md(fixtures_dir):
    return fixtures_dir / "manim_simple.md"


@pytest.fixture
def manim_complex_md(fixtures_dir):
    return fixtures_dir / "manim_complex.md"


@pytest.fixture
def animate_simple_md(fixtures_dir):
    return fixtures_dir / "animate_simple.md"


@pytest.fixture
def animate_positioning_md(fixtures_dir):
    return fixtures_dir / "animate_positioning.md"


@pytest.fixture
def animate_multi_animation_md(fixtures_dir):
    return fixtures_dir / "animate_multi_animation.md"


@pytest.fixture
def animate_malformed_md(fixtures_dir):
    return fixtures_dir / "animate_malformed.md"


@pytest.fixture
def work_dir(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    return work


@pytest.fixture
def copy_fixture_to_work(fixtures_dir, work_dir):
    def _copy(fixture_name: str) -> Path:
        src = fixtures_dir / fixture_name
        dst = work_dir / fixture_name
        shutil.copy2(src, dst)
        return dst

    return _copy
