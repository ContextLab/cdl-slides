"""Tests for cdl_slides.assets."""

import shutil
from pathlib import Path

from cdl_slides.assets import (
    _path_to_file_url,
    _rewrite_css_urls,
    copy_assets_alongside_output,
    get_assets_dir,
    get_fonts_dir,
    get_images_dir,
    get_js_dir,
    get_themes_dir,
    prepare_theme_for_compilation,
)


class TestGetAssetsDirExists:
    def test_assets_dir_is_directory(self):
        assets = get_assets_dir()
        assert assets.is_dir()

    def test_assets_dir_contains_subdirs(self):
        assets = get_assets_dir()
        assert (assets / "themes").is_dir()
        assert (assets / "fonts").is_dir()
        assert (assets / "images").is_dir()
        assert (assets / "js").is_dir()


class TestGetThemesDirHasCss:
    def test_cdl_theme_css_exists(self):
        themes = get_themes_dir()
        css = themes / "cdl-theme.css"
        assert css.is_file()
        content = css.read_text(encoding="utf-8")
        assert len(content) > 100


class TestGetFontsDirHasFonts:
    def test_avenir_fonts_present(self):
        fonts = get_fonts_dir()
        otf_files = list(fonts.glob("*.otf"))
        assert len(otf_files) >= 1

    def test_fira_code_fonts_present(self):
        fonts = get_fonts_dir()
        fira = list(fonts.glob("FiraCode-*.ttf"))
        assert len(fira) >= 1


class TestGetImagesDirHasSvgs:
    def test_arrow_svgs_exist(self):
        images = get_images_dir()
        svgs = list(images.glob("*.svg"))
        assert len(svgs) >= 1
        names = {s.name for s in svgs}
        assert "arrow-clean.svg" in names


class TestGetJsDirHasScripts:
    def test_js_files_exist(self):
        js_dir = get_js_dir()
        js_files = list(js_dir.glob("*.js"))
        assert len(js_files) >= 2
        names = {f.name for f in js_files}
        assert "chart-defaults.js" in names
        assert "chart-animations.js" in names


class TestRewriteCssUrlsFonts:
    def test_font_urls_rewritten(self):
        assets = get_assets_dir()
        css = "src: url('../../fonts/AvenirLTStd-Book.otf') format('opentype');"
        result = _rewrite_css_urls(css, assets)
        assert "file://" in result
        assert "AvenirLTStd-Book.otf" in result
        assert "../../fonts" not in result


class TestRewriteCssUrlsThemesKeptRelative:
    def test_theme_image_urls_stay_relative(self):
        assets = get_assets_dir()
        css = "background-image: url('themes/background_geometry.svg');"
        result = _rewrite_css_urls(css, assets)
        assert "file://" not in result
        assert "themes/background_geometry.svg" in result

    def test_conversation_png_stays_relative(self):
        assets = get_assets_dir()
        css = "background-image: url('themes/conversation_green_32pct.png');"
        result = _rewrite_css_urls(css, assets)
        assert "file://" not in result
        assert "themes/conversation_green_32pct.png" in result


class TestRewriteCssUrlsImagesKeptRelative:
    def test_arrow_svg_stays_relative(self):
        assets = get_assets_dir()
        css = "background: url('images/arrow-clean.svg') no-repeat center;"
        result = _rewrite_css_urls(css, assets)
        assert "file://" not in result
        assert "images/arrow-clean.svg" in result


class TestRewriteCssUrlsPreservesHttps:
    def test_https_urls_untouched(self):
        assets = get_assets_dir()
        css = "@import url('https://fonts.googleapis.com/css2?family=Fira+Code');"
        result = _rewrite_css_urls(css, assets)
        assert "https://fonts.googleapis.com" in result
        assert "file://" not in result

    def test_data_urls_untouched(self):
        assets = get_assets_dir()
        css = "background: url('data:image/png;base64,abc123');"
        result = _rewrite_css_urls(css, assets)
        assert "data:image/png" in result
        assert "file://" not in result


class TestPrepareThemeForCompilation:
    def test_creates_temp_dir_with_rewritten_css(self, tmp_path):
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        theme_dir = prepare_theme_for_compilation(work_dir)
        try:
            assert theme_dir.is_dir()
            css_file = theme_dir / "cdl-theme.css"
            assert css_file.is_file()
            content = css_file.read_text(encoding="utf-8")
            assert "file://" in content
            assert "../../fonts" not in content
        finally:
            shutil.rmtree(theme_dir, ignore_errors=True)

    def test_copies_themes_dir(self, tmp_path):
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        theme_dir = prepare_theme_for_compilation(work_dir)
        try:
            themes_subdir = theme_dir / "themes"
            assert themes_subdir.is_dir()
            assert (themes_subdir / "background_geometry.svg").is_file()
            assert (themes_subdir / "conversation_green_32pct.png").is_file()
            # CSS should NOT be in the themes subdir
            assert not (themes_subdir / "cdl-theme.css").exists()
        finally:
            shutil.rmtree(theme_dir, ignore_errors=True)

    def test_copies_images_dir(self, tmp_path):
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        theme_dir = prepare_theme_for_compilation(work_dir)
        try:
            images_subdir = theme_dir / "images"
            assert images_subdir.is_dir()
            assert (images_subdir / "arrow-clean.svg").is_file()
        finally:
            shutil.rmtree(theme_dir, ignore_errors=True)

    def test_theme_urls_relative_in_rewritten_css(self, tmp_path):
        work_dir = tmp_path / "work"
        work_dir.mkdir()
        theme_dir = prepare_theme_for_compilation(work_dir)
        try:
            css_content = (theme_dir / "cdl-theme.css").read_text(encoding="utf-8")
            assert "url('themes/background_geometry.svg')" in css_content
            assert "url('images/arrow-clean.svg')" in css_content
        finally:
            shutil.rmtree(theme_dir, ignore_errors=True)


class TestCopyAssetsAlongsideOutput:
    def test_copies_themes_and_images(self, tmp_path):
        html_file = tmp_path / "output.html"
        html_file.write_text("<html></html>")
        copy_assets_alongside_output(html_file)
        assert (tmp_path / "themes").is_dir()
        assert (tmp_path / "themes" / "background_geometry.svg").is_file()
        assert (tmp_path / "themes" / "conversation_green_32pct.png").is_file()
        assert (tmp_path / "images").is_dir()
        assert (tmp_path / "images" / "arrow-clean.svg").is_file()

    def test_does_not_copy_css_into_themes(self, tmp_path):
        html_file = tmp_path / "output.html"
        html_file.write_text("<html></html>")
        copy_assets_alongside_output(html_file)
        assert not (tmp_path / "themes" / "cdl-theme.css").exists()

    def test_skips_if_dirs_exist(self, tmp_path):
        html_file = tmp_path / "output.html"
        html_file.write_text("<html></html>")
        (tmp_path / "themes").mkdir()
        marker = tmp_path / "themes" / "marker.txt"
        marker.write_text("existing")
        copy_assets_alongside_output(html_file)
        # Should not overwrite existing dir
        assert marker.read_text() == "existing"


class TestPathToFileUrl:
    def test_unix_path(self):
        p = Path("/usr/local/share/fonts/test.otf")
        url = _path_to_file_url(p)
        assert url == "file:///usr/local/share/fonts/test.otf"

    def test_path_with_spaces(self):
        p = Path("/home/user/my fonts/test.otf")
        url = _path_to_file_url(p)
        assert "file://" in url
        assert "my fonts" in url
