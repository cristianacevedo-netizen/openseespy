"""Pruebas unitarias para viral_video_pipeline."""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from viral_video_pipeline import (
    APIRequestError,
    AppConfig,
    HedraVideoGenerator,
    PipelineError,
    ViralTrendAnalyzer,
    YouTubeShortsUploader,
)


class ViralVideoPipelineTests(unittest.TestCase):
    def test_rank_trends_combines_sources(self) -> None:
        sources = {
            "google_trends": ["IA generativa", "Futbol"],
            "youtube_trends": ["IA generativa", "Cocina rápida"],
            "tiktok_trends": ["futbol", "IA generativa"],
        }
        ranked = ViralTrendAnalyzer.rank_trends(sources, top_n=2)
        self.assertEqual(ranked[0]["keyword"], "IA generativa")
        self.assertEqual(ranked[0]["score"], 3)
        self.assertEqual(ranked[1]["keyword"].lower(), "futbol")

    def test_generate_script_requires_trends(self) -> None:
        generator = HedraVideoGenerator(AppConfig())
        with self.assertRaises(PipelineError):
            generator.generate_script([])

    def test_generate_script_uses_primary_trend(self) -> None:
        generator = HedraVideoGenerator(AppConfig())
        script = generator.generate_script(
            [
                {"keyword": "IA generativa", "score": 3, "sources": ["google_trends"]},
                {"keyword": "productividad", "score": 2, "sources": ["youtube_trends"]},
            ]
        )
        self.assertIn("IA generativa", script)
        self.assertIn("productividad", script)

    def test_config_loads_from_env(self) -> None:
        env = {
            "YOUTUBE_API_KEY": "abc",
            "HEDRA_API_KEY": "hedra",
            "OUTPUT_DIR": "tmp-output",
        }
        with patch.dict(os.environ, env, clear=False):
            config = AppConfig.from_env()
        self.assertEqual(config.youtube_api_key, "abc")
        self.assertEqual(config.hedra_api_key, "hedra")
        self.assertEqual(config.output_dir, "tmp-output")

    @patch("viral_video_pipeline.time.sleep", return_value=None)
    @patch("viral_video_pipeline._http_json")
    def test_create_video_timeout_raises(self, http_json_mock: MagicMock, _: MagicMock) -> None:
        config = AppConfig(hedra_api_key="k", hedra_avatar_id="a", hedra_voice_id="v")
        generator = HedraVideoGenerator(config)
        http_json_mock.side_effect = [{"job_id": "job-1"}] + [{"status": "processing"}] * 12
        with TemporaryDirectory() as tmp_dir:
            output_path = str(Path(tmp_dir) / "video.mp4")
            with self.assertRaises(APIRequestError):
                generator.create_video("script", output_path)

    @patch("viral_video_pipeline.request.urlopen")
    def test_upload_short_returns_video_id(self, urlopen_mock: MagicMock) -> None:
        config = AppConfig(youtube_access_token="token")
        uploader = YouTubeShortsUploader(config)
        with TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir) / "video.mp4"
            file_path.write_bytes(b"video-data")

            init_response = MagicMock()
            init_response.__enter__.return_value = SimpleNamespace(headers={"Location": "https://upload.local"})
            upload_response = MagicMock()
            upload_response.__enter__.return_value = SimpleNamespace(read=lambda: b'{"id":"abc123"}')
            urlopen_mock.side_effect = [init_response.__enter__.return_value, upload_response.__enter__.return_value]

            # wrap side effect in context-manager-compatible function
            def _urlopen_side_effect(*args, **kwargs):
                obj = urlopen_mock.side_effect_values.pop(0)

                class _Ctx:
                    def __enter__(self_inner):
                        return obj

                    def __exit__(self_inner, exc_type, exc, tb):
                        return False

                return _Ctx()

            urlopen_mock.side_effect_values = [
                init_response.__enter__.return_value,
                upload_response.__enter__.return_value,
            ]
            urlopen_mock.side_effect = _urlopen_side_effect

            video_id = uploader.upload_short(str(file_path), "t", "d", ["x"])
            self.assertEqual(video_id, "abc123")


if __name__ == "__main__":
    unittest.main()
