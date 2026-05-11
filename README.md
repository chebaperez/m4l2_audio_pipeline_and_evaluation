# M4L2: Audio Pipelines y Evaluación en AI

Este repositorio contiene una implementación práctica de un pipeline de audio para transcripción, resumen automático y evaluación de precisión utilizando los servicios de **OpenAI** y métricas estándar de la industria.

## Descripción

El script `audio_summary.py` permite procesar archivos de audio para:
1. **Transcripción (ASR):** Convierte voz a texto utilizando `whisper-1` de OpenAI.
2. **Resumen:** Genera un resumen conciso y coherente del texto transcrito utilizando `gpt-4o-mini`.
3. **Evaluación (WER):** Calcula el **Word Error Rate (WER)** comparando la transcripción generada contra un texto de referencia (ground truth), permitiendo medir objetivamente la calidad del pipeline.

A diferencia de las implementaciones locales, este script utiliza APIs en la nube, lo que facilita el despliegue y elimina la necesidad de hardware especializado.

## Requisitos Previos

- Python 3.12 o superior.
- Una cuenta de OpenAI con una clave de API válida.

## Configuración

1. **Crear el entorno virtual:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno:**
   
   Copia el archivo `.env_example` a un nuevo archivo llamado `.env`:
   ```bash
   cp .env_example .env
   ```
   Edita el archivo `.env` y coloca tu `OPENAI_API_KEY`.

## Estructura del Proyecto

- `audio_summary.py`: Script principal que integra ASR, resumen y evaluación.
- `requirements.txt`: Dependencias del proyecto (`openai`, `python-dotenv`, `jiwer`).
- `resources/`: Carpeta con audios de prueba y textos de referencia.
- `.env_example`: Plantilla para la configuración de la API Key.
- `.gitignore`: Configuración para excluir archivos sensibles.

### Estructura de Recursos

El directorio `resources/` contiene archivos de prueba con diferentes niveles de calidad para experimentar con el pipeline y su evaluación:

- `support_call_clean.wav`: Audio limpio de referencia.
- `support_call_white_noise.wav`: Audio con ruido de fondo.
- `support_call_cutted.wav`: Audio degradado.
- `support_call_destroyed.wav`: Audio con degradación severa.
- `original_text.txt`: Transcripción manual (ground truth) para evaluar el WER.

## Uso

### Transcripción y Resumen (Básico)
Ejecuta el script principal con los valores por defecto:
```bash
python audio_summary.py
```

### Especificar un audio diferente
```bash
python audio_summary.py --audio "resources/support_call_white_noise.wav"
```

### Evaluación de Precisión (WER)
Para evaluar la calidad de la transcripción comparándola con el texto original:
```bash
python audio_summary.py --wer "resources/original_text.txt"
python audio_summary.py --audio "resources/support_call_white_noise.wav" --wer "resources/original_text.txt"
```

