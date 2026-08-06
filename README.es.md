> Traducción comunitaria (borrador) — Política P2-002 de NTARI, Difusión
> Global Multilingüe. Fuente: README.md (original en inglés, instantánea del
> 2026-07-29). Borrador comunitario asistido por máquina, pendiente de
> revisión por el mantenedor regional conforme a P2-002 §3.1. Las
> especificaciones técnicas centrales permanecen en inglés conforme a §2.2.
>
> ¿Encontraste un error en esta traducción? Tu corrección es una contribución
> bienvenida y valorada: haz un fork del repositorio y abre un pull request en
> https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale.

# Escala de Evaluación Comercial Basada en Leveson (LBTAS)

Un sistema de calificación para el comercio digital basado en la metodología de evaluación de software aeronáutico de Nancy Leveson, con criterios de evaluación bidireccional.

## Descripción general

La Escala de Evaluación Comercial Basada en Leveson (LBTAS, por sus siglas en inglés) implementa la metodología de evaluación de software aeronáutico de Nancy Leveson, desarrollada para aplicaciones aeroespaciales, adaptada a contextos de comercio digital y evaluación económica. LBTAS proporciona un marco para capturar datos de calidad de transacciones utilizando una escala de 6 puntos.

## El problema de los sistemas de calificación tradicionales

Los sistemas de 5 estrellas no proporcionan datos que motiven la mejora del productor. El sistema de 5 estrellas fue desarrollado en 1958 por Forbes Travel Guide (anteriormente Mobil Travel Guide) para publicitar la calidad de los hoteles a lo largo de las carreteras interestatales de EE. UU. Fue diseñado como un sistema de comunicación unidireccional para viajes por carretera, no para el comercio digital.

**Limitaciones:**
- Las calificaciones aportan un valor limitado en contextos de comercio electrónico
- Los gerentes de relaciones públicas crean barreras al cambio de políticas
- La granularidad no logra capturar la complejidad de las transacciones
- La evaluación unidireccional ignora la responsabilidad del consumidor
- La insuficiencia de datos obliga a depender de las secciones de comentarios

## ¿Por qué el enfoque Leveson?

El Sistema Leveson se origina en el desarrollo de software aeronáutico, donde las fallas del sistema resultan en pérdida de vidas o en inversión desperdiciada en I+D. Esta metodología:

- Utiliza una escala de 6 puntos (de +4 a -1) con definiciones por categoría
- Comprime el significado en cada nivel de calificación
- Reduce la dependencia de las secciones de comentarios para obtener datos
- Permite la evaluación bidireccional (tanto del productor como del consumidor)
- Respalda ciclos de mejora basados en datos

## Definiciones de la escala

### +4 **Deleite**
La interacción anticipa la evolución de las prácticas y preocupaciones del usuario después de la transacción

### +3 **Sin consecuencias negativas**
Interacción diseñada para prevenir pérdidas, superando los estándares básicos de calidad

### +2 **Satisfacción básica**
La interacción cumple con estándares socialmente aceptables, superando las demandas expresadas por el usuario

### +1 **Promesa básica**
La interacción cumple con todas las demandas expresadas por el usuario, nada más

### 0 **Satisfacción cínica**
La interacción cumple una promesa básica que requiere poca o ninguna disciplina orientada a la satisfacción del usuario

### -1 **Sin confianza**
El usuario fue perjudicado, explotado o recibió un producto/servicio con evidencia de falta de disciplina o intención maliciosa

## Evaluación bidireccional

LBTAS permite la rendición de cuentas en ambas direcciones dentro de las redes digitales al mantener calificaciones tanto para:

- **Productores**: Identifica a los proveedores
- **Consumidores**: Identifica a los clientes

Este enfoque facilita la autorregulación comunitaria y reduce la necesidad de moderación centralizada.

## Cómo leer la reputación

Las calificaciones nunca se promedian. Una reputación es el conteo de calificaciones recibidas en cada nivel (de `-1` a `+4`) más el total. El total importa por sí solo: refleja el volumen de transacciones y, de manera indirecta, el tiempo en servicio. Una distribución limpia sobre 5,000 calificaciones es una señal más fuerte que la misma forma sobre 5 — y promediar borraría esa diferencia al colapsar ambas en el mismo número. (El conteo es un conteo de calificaciones; las cifras precisas de transacciones y antigüedad provienen de la API, que registra la fecha y hora de cada evento de calificación.)

Un `-1` ("Sin confianza") nunca se diluye: el comando `report` muestra cada intercambio que ha recibido una o más calificaciones de `-1` en una lista `harm_flagged`, y `list` añade una marca de daño a cualquier intercambio con un `-1`.

## Características

- **Metodología**: Basada en marcos de evaluación aeroespaciales
- **Evaluación bidireccional**: Califica a ambas partes de las transacciones
- **Granularidad**: Escala de 6 puntos con definiciones
- **Dependencias**: Integración en sistemas
- **Soporte de base de datos**: Soporte para capa de persistencia
- **Código abierto**: Desarrollo y personalización impulsados por la comunidad

## Instalación

```bash
# Clone the repository
git clone https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale.git
cd Leveson-Based-Trade-Assessment-Scale

# Make executable (optional)
chmod +x lbtas.py

# Run directly
python3 lbtas.py --help
```

No se requieren dependencias externas. Utiliza únicamente la biblioteca estándar de Python 3.

## Inicio rápido

```python
from lbtas import LevesonRatingSystem

# Initialize the rating system
rating_system = LevesonRatingSystem()

# Add an exchange (transaction)
rating_system.add_exchange("transaction_001")

# Add ratings (categories: reliability, usability, performance, support)
rating_system.add_rating(
    exchange_name="transaction_001",
    criterion="reliability",
    rating=3  # No Negative Consequences
)

# Read the distribution (ratings are never averaged)
ratings = rating_system.view_ratings("transaction_001")
print(ratings["reliability"])
# {'distribution': {'-1': 0, '0': 0, '1': 0, '2': 0, '3': 1, '4': 0}, 'total': 1}
```

### Interfaz de línea de comandos

```bash
# Interactive rating
python3 lbtas.py rate --exchange "MyService"

# Programmatic rating
python3 lbtas.py add --exchange "MyService" --criterion reliability --rating 3

# View ratings
python3 lbtas.py view --exchange "MyService"

# Generate report
python3 lbtas.py report

# Export data
python3 lbtas.py export --format json --output ratings.json
```

## Almacenamiento

LBTAS utiliza almacenamiento en archivos JSON para la persistencia:

```python
# Initialize with storage file
rating_system = LevesonRatingSystem(storage_file='ratings.json')

# Ratings are saved automatically to the file
rating_system.add_exchange("service_001")
rating_system.add_rating("service_001", "reliability", 3)
```

Formato del archivo de almacenamiento:
```json
{
  "service_001": {
    "reliability": [3, 4, 3],
    "usability": [2, 3],
    "performance": [4],
    "support": [3, 3, 2],
    "_metadata": {
      "created": "2024-09-04T10:30:00",
      "total_ratings": 10
    }
  }
}
```

### Categorías de calificación

Categorías predeterminadas:
- **Reliability** (confiabilidad): Fiabilidad y consistencia
- **Usability** (usabilidad): Facilidad de uso y experiencia del usuario
- **Performance** (rendimiento): Velocidad y eficiencia
- **Support** (soporte): Calidad del servicio al cliente

Se pueden definir categorías personalizadas durante la inicialización.

## Casos de uso

### Investigación académica
- Estudiar cómo el diseño de la escala de calificación afecta el comportamiento del usuario y los resultados del mercado
- Medir los efectos de la evaluación bidireccional sobre la confianza y la cooperación
- Analizar alternativas de evaluación basadas en calidad frente a otros marcos

### Plataformas de comercio electrónico
- Implementar métricas de calidad para transacciones en marketplaces
- Habilitar sistemas de reputación impulsados por la comunidad
- Reducir la carga de moderación mediante la autorregulación

### Cooperativas digitales
- Facilitar la rendición de cuentas entre pares
- Respaldar estructuras de gobernanza
- Permitir mejoras de políticas basadas en datos

## Arquitectura

LBTAS está implementado como un único módulo de Python con:

1. **Clase principal**: `LevesonRatingSystem` gestiona las calificaciones y el almacenamiento
2. **Persistencia JSON**: Almacenamiento basado en archivos con guardado automático
3. **Interfaz CLI**: Herramienta de línea de comandos para uso interactivo y programático
4. **Sin dependencias externas**: Utiliza únicamente la biblioteca estándar de Python

El sistema admite:
- Recolección interactiva de calificaciones
- Envío programático de calificaciones
- Categorías de calificación personalizadas
- Generación de reportes y exportación de datos

## Documentación

- [Documentación completa](docs/README.md)
- [Referencia de la API](docs/api.md)
- [Guía de integración](docs/integration.md)
- [Aplicaciones de investigación](docs/research.md)

## Cómo contribuir

Las contribuciones se realizan a través del espacio de trabajo de NTARI en Slack:

**Únete a la conversación**: https://ntari.slack.com/archives/C09N88JN2SH

Consulta nuestras [Pautas de contribución](CONTRIBUTING.md) para conocer:

- Estilo y estándares de código
- Requisitos de pruebas
- Proceso de pull requests
- Código de conducta de la comunidad

## Investigación y desarrollo

Este programa fue producido por el **Forge Laboratory del Network Theory Applied Research Institute** (ahora NTARI Research & Development) por Jodson B. Graves utilizando ChatGPT-3 el 4 de septiembre de 2024.

### Acerca de NTARI Research & Development

NTARI Research & Development es el programa de desarrollo de software de NTARI para crear sistemas y protocolos digitales que aprovechan la teoría de redes para potenciar las capacidades cooperativas a través de internet. Desarrollamos herramientas, plataformas y marcos de código abierto que empoderan a las comunidades para construir ecosistemas en línea.

**Conoce más y apoya a NTARI**: [https://ntari.org](https://ntari.org)

## Cita

Si utilizas LBTAS en tu investigación, por favor cita:

```bibtex
@software{lbtas2024,
  title={Leveson-Based Trade Assessment Scale},
  author={Graves, Jodson B.},
  organization={Network Theory Applied Research Institute},
  year={2024},
  url={https://github.com/NTARI-OpenCoreLab/Leveson-Based-Trade-Assessment-Scale}
}
```

## Referencias

- Leveson, N. G. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press.
- Leveson, N. G. (2020). *CAST Handbook: How to Learn More from Incidents and Accidents*. MIT.

## Licencia

Este proyecto está licenciado bajo la GNU Affero General Public License v3.0 (AGPL-3.0) — consulta el archivo [LICENSE](LICENSE) para más detalles.

La licencia AGPL-3.0 requiere que:
- El código fuente debe estar disponible cuando el software se utiliza a través de una red
- Las modificaciones deben publicarse bajo la misma licencia
- Los cambios deben documentarse
- El uso en red se considera distribución

## Agradecimientos

- **Nancy Leveson** - Desarrollo de la metodología original
- **NTARI Research & Development** - Investigación e implementación
- **Comunidad de código abierto** - Contribuciones y retroalimentación

---

**Mantenido por**: [NTARI Research & Development](https://ntari.org)  
**¿Preguntas?** Abre un issue o contáctanos en info@ntari.org
