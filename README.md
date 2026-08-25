# openseespy
revision y creacion de codigos

## Nuevo módulo: `viral_video_pipeline.py`

Se agregó un programa en Python con 3 funcionalidades:

1. Análisis de viralidad global (Google Trends RSS, TikTok trends, YouTube trends).
2. Generación de script y video corto con Hedra API.
3. Subida automática a YouTube Data API v3 con título, descripción y tags basados en tendencias.

### Configuración segura (variables de entorno)

```bash
export GOOGLE_TRENDS_RSS_URL="https://trends.google.com/trending/rss?geo=US"
export TIKTOK_TRENDS_URL="https://open.tiktokapis.com/v2/research/video/query/"
export TIKTOK_API_TOKEN="tu_token_tiktok"
export YOUTUBE_API_KEY="tu_api_key_youtube"
export YOUTUBE_ACCESS_TOKEN="tu_access_token_oauth_youtube"
export HEDRA_API_KEY="tu_api_key_hedra"
export HEDRA_API_BASE_URL="https://api.hedra.com"
export HEDRA_AVATAR_ID="avatar_id"
export HEDRA_VOICE_ID="voice_id"
export OUTPUT_DIR="outputs"
```

### Ejemplo de uso

```bash
python viral_video_pipeline.py
```

### Pruebas del módulo

```bash
python -m unittest test_viral_video_pipeline
```
