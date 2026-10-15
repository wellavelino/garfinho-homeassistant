import io
import json
import zipfile

import pytest

from garfinho_client.content import clean_html, parse_bundle
from garfinho_client.exceptions import ApiError


def bundle(rows) -> bytes:
    js = "var offlineDataDump = " + json.dumps({"result": rows}) + ";\nvar other = [];"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("app.js", js)
    return buf.getvalue()


def row(recipe_id, content, tag="recipes"):
    return {"id": "x", "tag": tag, "data": {"localRecordId": recipe_id, "content": content}}


def test_keeps_formatting_and_drops_attributes_and_images():
    c = clean_html(
        '<h4 style="color:red"><span>Como preparar:</span></h4>'
        '<ol class="a"><li>Misture&nbsp;tudo</li></ol><p><img src="x.png"></p>'
    )
    assert c.html == "<h4>Como preparar:</h4><ol><li>Misture tudo</li></ol>"


def test_escapes_text_and_drops_scripts():
    c = clean_html("<p>a &lt;b&gt;</p><script>alert(1)</script><p onclick='x()'>ok</p>")
    assert c.html == "<p>a &lt;b&gt;</p><p>ok</p>"


def test_skips_blocks_hidden_in_the_app():
    c = clean_html('<p>visible</p><div class="bf-wysiwyg-hide-app"><p>web only</p></div><p>end</p>')
    assert c.html == "<p>visible</p><p>end</p>"


def test_finds_youtube_video():
    c = clean_html('<p>x</p><iframe src="https://www.youtube.com/embed/8txLsesNgl4"></iframe>')
    assert c.video_id == "8txLsesNgl4"
    assert "iframe" not in c.html


def test_parse_bundle_maps_recipe_ids_and_ignores_other_tags():
    out = parse_bundle(bundle([row("r1", "<p>one</p>"), row("r2", "<p>no</p>", tag="cookbook")]))
    assert list(out) == ["r1"]
    assert out["r1"].html == "<p>one</p>"


def test_parse_bundle_rejects_garbage():
    with pytest.raises(ApiError):
        parse_bundle(b"not a zip")
