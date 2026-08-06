> Traducción comunitaria (borrador) — Política NTARI P2-002, Difusión Multilingüe Global. Fuente: contributing.md (original en inglés, captura del 2026-07-29). Borrador comunitario asistido por máquina, pendiente de revisión por el mantenedor regional conforme a P2-002 §3.1. Las especificaciones técnicas centrales permanecen en inglés conforme a §2.2.
>
> ¿Encontraste un error en esta traducción? Tu corrección es una contribución
> bienvenida y valorada: haz un fork del repositorio y abre un pull request en
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

# Cómo contribuir a LBTAS

## Cómo contribuir

Las contribuciones se realizan a través del espacio de trabajo de Slack de NTARI.

**Únete a la discusión**: https://ntari.slack.com/archives/C09N88JN2SH

## Tipos de contribuciones

### Contribuciones de código
- Corrección de bugs
- Implementación de funcionalidades
- Mejoras de rendimiento
- Actualizaciones de documentación

### Contribuciones de investigación
- Estudios de casos de uso
- Artículos académicos que utilicen LBTAS
- Ejemplos de integración
- Análisis de la efectividad de las calificaciones

### Contribuciones comunitarias
- Reporte de issues
- Sugerencias de funcionalidades
- Mejoras a la documentación
- Apoyo con traducciones

## Proceso de desarrollo

### 1. Discusión
Discute los cambios que propones en el canal de Slack antes de comenzar a trabajar.

### 2. Fork y branch
```bash
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale
git checkout -b feature/your-feature-name
```

### 3. Estándares de código

**Estilo de Python**
- Sigue PEP 8
- Usa type hints
- Incluye docstrings en todas las funciones y clases
- Mantén las funciones enfocadas y con menos de 50 líneas

**Estilo de documentación**
- Escribe en un lenguaje técnico y factual
- Evita adjetivos y adverbios
- Incluye ejemplos de código
- Prueba todos los ejemplos

### 4. Pruebas

Prueba tus cambios:
```bash
# Test basic functionality
python3 lbtas.py rate --exchange "TestService"
python3 lbtas.py view --exchange "TestService"
python3 lbtas.py report

# Test as library
python3 -c "from lbtas import LevesonRatingSystem; rs = LevesonRatingSystem(); rs.add_exchange('test'); print('OK')"
```

### 5. Mensajes de commit

Formato: `type: brief description`

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en la documentación
- `refactor`: Reestructuración de código
- `test`: Adición o modificación de pruebas
- `chore`: Tareas de mantenimiento

Ejemplos:
```
feat: add CSV export format
fix: handle empty rating lists in report
docs: update installation instructions
```

### 6. Pull request

1. Haz push de tu branch a tu fork
2. Abre un pull request hacia el branch main
3. Referencia cualquier issue relacionado
4. Describe los cambios realizados y su justificación
5. Espera la revisión y la discusión en Slack

## Código de conducta

### Estándares

- Respeta a todas las personas que contribuyen
- Enfócate en el mérito técnico
- Ofrece retroalimentación constructiva
- Acepta las críticas a tus contribuciones
- Prioriza los objetivos del proyecto por encima de las preferencias personales

### Conductas prohibidas

- Ataques personales o acoso
- Lenguaje o comportamiento discriminatorio
- Trolling o comentarios provocadores
- Compartir información privada de otras personas
- Conducta no ética o poco profesional

### Aplicación

Las violaciones pueden resultar en:
1. Advertencia
2. Suspensión temporal del proyecto
3. Expulsión permanente del proyecto

Reporta violaciones a: forge@ntari.org

## Licencia

Al contribuir, aceptas que tus contribuciones se licenciarán bajo AGPL-3.0.

Todas las contribuciones deben:
- Ser trabajo original tuyo o estar debidamente atribuidas
- No violar derechos de terceros
- Cumplir con los requisitos de AGPL-3.0

## Preguntas

Para preguntas sobre cómo contribuir:
1. Pregunta en Slack: https://ntari.slack.com/archives/C09N88JN2SH
2. Abre un issue en GitHub
3. Escribe a: forge@ntari.org

## Reconocimiento

Las personas que contribuyen son reconocidas en:
- El historial de commits de Git
- Las notas de versión (release notes)
- La documentación del proyecto

Tipos de contribución reconocidos:
- Contribuciones de código (commits)
- Contribuciones de investigación (citas)
- Contribuciones de documentación (créditos de documentación)
- Apoyo comunitario (agradecimientos)
