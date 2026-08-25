"""Pruebas unitarias para viral_video_pipeline."""

import os
import unittest
from unittest.mock import patch

from viral_video_pipeline import AppConfig, HedraVideoGenerator, PipelineError, ViralTrendAnalyzer


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


if __name__ == "__main__":
    unittest.main()
