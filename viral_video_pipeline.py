"""Pipeline para detectar tendencias virales, crear un corto con Hedra y subirlo a YouTube."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error, parse, request


LOGGER = logging.getLogger(__name__)
DEFAULT_GOOGLE_TRENDS_RSS_URL = "https://trends.google.com/trending/rss?geo=US"
DEFAULT_TIKTOK_TRENDS_URL = "https://open.tiktokapis.com/v2/research/video/query/"
DEFAULT_HEDRA_API_BASE_URL = "https://api.hedra.com"


class PipelineError(Exception):
    """Error base del pipeline."""


class ConfigError(PipelineError):
    """Error de configuración."""


class APIRequestError(PipelineError):
    """Error de llamada a API externa."""


@dataclass
class AppConfig:
    """Configuración cargada desde variables de entorno."""

    google_trends_rss_url: str = DEFAULT_GOOGLE_TRENDS_RSS_URL
    tiktok_trends_url: str = DEFAULT_TIKTOK_TRENDS_URL
    tiktok_api_token: str = ""
    youtube_api_key: str = ""
    youtube_access_token: str = ""
    hedra_api_key: str = ""
    hedra_api_base_url: str = DEFAULT_HEDRA_API_BASE_URL
    hedra_avatar_id: str = ""
    hedra_voice_id: str = ""
    output_dir: str = "outputs"

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Construye la configuración desde variables de entorno."""
        return cls(
            google_trends_rss_url=os.getenv("GOOGLE_TRENDS_RSS_URL", DEFAULT_GOOGLE_TRENDS_RSS_URL),
            tiktok_trends_url=os.getenv("TIKTOK_TRENDS_URL", DEFAULT_TIKTOK_TRENDS_URL),
            tiktok_api_token=os.getenv("TIKTOK_API_TOKEN", ""),
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", ""),
            youtube_access_token=os.getenv("YOUTUBE_ACCESS_TOKEN", ""),
            hedra_api_key=os.getenv("HEDRA_API_KEY", ""),
            hedra_api_base_url=os.getenv("HEDRA_API_BASE_URL", DEFAULT_HEDRA_API_BASE_URL),
            hedra_avatar_id=os.getenv("HEDRA_AVATAR_ID", ""),
            hedra_voice_id=os.getenv("HEDRA_VOICE_ID", ""),
            output_dir=os.getenv("OUTPUT_DIR", "outputs"),
        )


def _safe_get(data: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    """Obtiene campos anidados sin lanzar excepciones."""
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _http_json(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Dict[str, Any]] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """Ejecuta una solicitud HTTP JSON simple."""
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(url=url, data=body, method=method)
    request_headers = {"Content-Type": "application/json", **(headers or {})}
    for key, value in request_headers.items():
        req.add_header(key, value)
    try:
        with request.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise APIRequestError(f"HTTP {exc.code} en {url}: {detail}") from exc
    except (error.URLError, json.JSONDecodeError) as exc:
        raise APIRequestError(f"Error consultando {url}: {exc}") from exc


def _auth_header(token: str) -> Dict[str, str]:
    """Crea encabezado Authorization tipo Bearer."""
    return {"Authorization": "Bearer " + token}


class ViralTrendAnalyzer:
    """Analiza tendencias virales globales desde Google, TikTok y YouTube."""

    def __init__(self, config: AppConfig):
        self.config = config

    def get_google_trends(self, limit: int = 10) -> List[str]:
        """Recupera tendencias desde el RSS público de Google Trends."""
        req = request.Request(self.config.google_trends_rss_url, method="GET")
        try:
            with request.urlopen(req, timeout=30) as response:
                xml_data = response.read().decode("utf-8", errors="ignore")
        except error.URLError as exc:
            raise APIRequestError(f"No se pudo consultar Google Trends: {exc}") from exc
        terms: List[str] = []
        for chunk in xml_data.split("<item>")[1:]:
            if "<title>" not in chunk:
                continue
            title = chunk.split("<title>", 1)[1].split("</title>", 1)[0].strip()
            if title:
                terms.append(title)
        return terms[:limit]

    def get_youtube_trends(self, limit: int = 10) -> List[str]:
        """Recupera temas virales desde YouTube Data API v3."""
        if not self.config.youtube_api_key:
            LOGGER.warning("YOUTUBE_API_KEY no configurada; se omite YouTube trends.")
            return []
        params = parse.urlencode(
            {
                "part": "snippet",
                "type": "video",
                "q": "shorts",
                "order": "viewCount",
                "maxResults": str(limit),
                "key": self.config.youtube_api_key,
            }
        )
        endpoint = f"https://www.googleapis.com/youtube/v3/search?{params}"
        data = _http_json(endpoint)
        return [
            _safe_get(item, ["snippet", "title"], "")
            for item in data.get("items", [])
            if _safe_get(item, ["snippet", "title"], "")
        ]

    def get_tiktok_trends(self, limit: int = 10) -> List[str]:
        """Recupera ideas de tendencias usando endpoint de TikTok configurado."""
        if not self.config.tiktok_api_token:
            LOGGER.warning("TIKTOK_API_TOKEN no configurada; se omite TikTok trends.")
            return []
        headers = _auth_header(self.config.tiktok_api_token)
        payload = {"max_count": limit}
        data = _http_json(
            self.config.tiktok_trends_url,
            method="POST",
            headers=headers,
            payload=payload,
        )
        trends: List[str] = []
        for item in data.get("data", {}).get("videos", []):
            text = item.get("title") or item.get("desc") or ""
            if text:
                trends.append(text)
        return trends[:limit]

    @staticmethod
    def rank_trends(sources: Dict[str, List[str]], top_n: int = 10) -> List[Dict[str, Any]]:
        """Combina tendencias por frecuencia para priorizar oportunidades."""
        scores: Dict[str, Dict[str, Any]] = {}
        for source_name, terms in sources.items():
            for term in terms:
                norm = term.strip().lower()
                if not norm:
                    continue
                if norm not in scores:
                    scores[norm] = {"keyword": term.strip(), "score": 0, "sources": set()}
                scores[norm]["score"] += 1
                scores[norm]["sources"].add(source_name)
        ranked = sorted(scores.values(), key=lambda x: (-x["score"], x["keyword"]))
        result: List[Dict[str, Any]] = []
        for entry in ranked[:top_n]:
            result.append(
                {
                    "keyword": entry["keyword"],
                    "score": entry["score"],
                    "sources": sorted(entry["sources"]),
                }
            )
        return result

    def analyze_global_virality(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """Ejecuta el análisis global consolidado."""
        sources = {
            "google_trends": self.get_google_trends(),
            "youtube_trends": self.get_youtube_trends(),
            "tiktok_trends": self.get_tiktok_trends(),
        }
        ranked = self.rank_trends(sources, top_n=top_n)
        LOGGER.info("Tendencias analizadas: %s", ranked[:3])
        return ranked


class HedraVideoGenerator:
    """Genera script dinámico y video corto usando Hedra API."""

    def __init__(self, config: AppConfig):
        self.config = config

    def generate_script(self, ranked_trends: List[Dict[str, Any]], duration_seconds: int = 30) -> str:
        """Crea un script corto basado en tendencias."""
        if not ranked_trends:
            raise PipelineError("No hay tendencias para generar el script.")
        selected = ranked_trends[0]["keyword"]
        secondary = ", ".join(item["keyword"] for item in ranked_trends[1:4] if "keyword" in item)
        script = (
            f"¡Hoy en {duration_seconds} segundos! Tema viral: {selected}. "
            f"Te cuento por qué está explotando globalmente y cómo se conecta con {secondary}. "
            "Si quieres más tendencias en tiempo real, sígueme para el próximo corto."
        )
        return script

    def create_video(self, script: str, output_path: str, duration_seconds: int = 30) -> str:
        """Solicita a Hedra generar video y descarga el resultado."""
        required = {
            "HEDRA_API_KEY": self.config.hedra_api_key,
            "HEDRA_AVATAR_ID": self.config.hedra_avatar_id,
            "HEDRA_VOICE_ID": self.config.hedra_voice_id,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ConfigError(f"Faltan variables para Hedra: {', '.join(missing)}")
        endpoint = f"{self.config.hedra_api_base_url.rstrip('/')}/v1/videos"
        payload = {
            "avatar_id": self.config.hedra_avatar_id,
            "voice_id": self.config.hedra_voice_id,
            "script": script,
            "duration_seconds": duration_seconds,
            "format": "mp4",
        }
        headers = _auth_header(self.config.hedra_api_key)
        creation = _http_json(endpoint, method="POST", headers=headers, payload=payload)
        job_id = creation.get("id") or creation.get("job_id")
        if not job_id:
            raise APIRequestError(f"Hedra no devolvió job_id válido: {creation}")
        status_endpoint = f"{endpoint}/{job_id}"
        video_url = ""
        max_attempts = 12
        timed_out = True
        for attempt in range(max_attempts):
            status = _http_json(status_endpoint, method="GET", headers=headers)
            state = status.get("status")
            if state == "completed":
                video_url = status.get("video_url") or _safe_get(status, ["output", "video_url"], "")
                timed_out = False
                break
            if state in {"failed", "error"}:
                raise APIRequestError(f"Hedra reportó error para job {job_id}: {status}")
            if attempt < max_attempts - 1:
                time.sleep(5)
        if not video_url:
            if timed_out:
                raise APIRequestError(f"Timeout esperando finalización de Hedra para job {job_id}")
            raise APIRequestError(f"Hedra finalizó job {job_id} sin video_url")
        file_path = Path(output_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with request.urlopen(video_url, timeout=60) as response:
                file_path.write_bytes(response.read())
        except error.URLError as exc:
            raise APIRequestError(f"No se pudo descargar el video generado: {exc}") from exc
        return str(file_path)


class YouTubeShortsUploader:
    """Sube videos a YouTube Data API v3 usando upload resumable."""

    def __init__(self, config: AppConfig):
        self.config = config

    def upload_short(self, file_path: str, title: str, description: str, tags: List[str]) -> str:
        """Sube un video y devuelve el ID de YouTube."""
        if not self.config.youtube_access_token:
            raise ConfigError("Falta YOUTUBE_ACCESS_TOKEN para subir a YouTube.")
        file_bytes = Path(file_path).read_bytes()
        query = parse.urlencode({"uploadType": "resumable", "part": "snippet,status"})
        init_url = f"https://www.googleapis.com/upload/youtube/v3/videos?{query}"
        metadata = {
            "snippet": {"title": title, "description": description, "tags": tags, "categoryId": "22"},
            "status": {"privacyStatus": "public"},
        }
        init_req = request.Request(init_url, method="POST", data=json.dumps(metadata).encode("utf-8"))
        init_req.add_header("Authorization", _auth_header(self.config.youtube_access_token)["Authorization"])
        init_req.add_header("Content-Type", "application/json; charset=UTF-8")
        init_req.add_header("X-Upload-Content-Type", "video/mp4")
        init_req.add_header("X-Upload-Content-Length", str(len(file_bytes)))
        try:
            with request.urlopen(init_req, timeout=30) as init_resp:
                upload_url = init_resp.headers.get("Location", "")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise APIRequestError(f"Error inicializando upload YouTube: {detail}") from exc
        if not upload_url:
            raise APIRequestError("No se recibió URL de upload resumable desde YouTube.")
        upload_req = request.Request(upload_url, method="PUT", data=file_bytes)
        upload_req.add_header("Authorization", _auth_header(self.config.youtube_access_token)["Authorization"])
        upload_req.add_header("Content-Type", "video/mp4")
        upload_req.add_header("Content-Length", str(len(file_bytes)))
        try:
            with request.urlopen(upload_req, timeout=120) as upload_resp:
                response_data = json.loads(upload_resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise APIRequestError(f"Error subiendo video a YouTube: {detail}") from exc
        video_id = response_data.get("id")
        if not video_id:
            raise APIRequestError(f"YouTube no devolvió id de video: {response_data}")
        return video_id


class ViralShortsPipeline:
    """Orquestador principal del flujo completo."""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or AppConfig.from_env()
        self.analyzer = ViralTrendAnalyzer(self.config)
        self.generator = HedraVideoGenerator(self.config)
        self.uploader = YouTubeShortsUploader(self.config)

    def run(self) -> Dict[str, Any]:
        """Ejecuta análisis, generación y subida."""
        trends = self.analyzer.analyze_global_virality(top_n=10)
        script = self.generator.generate_script(trends, duration_seconds=30)
        title = f"Short viral: {trends[0]['keyword'][:70]}"
        description = (
            f"Tendencia detectada globalmente: {trends[0]['keyword']}\n\n"
            f"Script generado automáticamente:\n{script}"
        )
        tags = [item["keyword"] for item in trends[:5]]
        video_path = str(Path(self.config.output_dir) / "viral_short.mp4")
        generated_path = self.generator.create_video(script, video_path, duration_seconds=30)
        youtube_video_id = self.uploader.upload_short(
            file_path=generated_path,
            title=title,
            description=description,
            tags=tags,
        )
        result = {
            "trends": trends,
            "script": script,
            "generated_video_path": generated_path,
            "youtube_video_id": youtube_video_id,
            "youtube_url": f"https://www.youtube.com/watch?v={youtube_video_id}",
        }
        LOGGER.info("Pipeline completado: %s", result["youtube_url"])
        return result


def configure_logging(level: int = logging.INFO) -> None:
    """Configura logging para ejecución CLI."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def run_example() -> None:
    """Ejemplo de uso del pipeline completo."""
    configure_logging()
    pipeline = ViralShortsPipeline()
    try:
        result = pipeline.run()
    except PipelineError as exc:
        LOGGER.error("Falló el pipeline: %s", exc)
        raise
    print("Video publicado:", result["youtube_url"])


if __name__ == "__main__":
    run_example()
