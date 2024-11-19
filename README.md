# DemoDay
## Descripción del Proyecto

Este proyecto implementa un sistema de captura y sincronización de datos EEG en tiempo real utilizando **LSL (Lab Streaming Layer)** y BrainFlow. Consiste en un experimento donde se presentan estímulos visuales intermitentes (flickers) y se registran simultáneamente señales EEG y marcadores de eventos en archivos separados para su análisis posterior.

### Componentes Principales:
1. **Emisor de Estímulos**:
   - Presenta estímulos visuales con frecuencias específicas utilizando *Psychopy*.
   - Envia marcadores a un flujo LSL indicando el inicio de cada estímulo.
   - Transmite las señales EEG en tiempo real desde un dispositivo OpenBCI.

2. **Listener de Datos**:
   - Captura datos EEG y marcadores en flujos LSL separados.
   - Guarda los datos en archivos CSV (`eeg_data.csv` y `markers.csv`) para análisis offline.

### Características:
- Sincronización precisa entre los datos EEG y los marcadores.
- Configuración modular que permite personalizar las frecuencias de estímulo y la duración del experimento.
- Compatible con dispositivos OpenBCI y flujos de datos sintéticos para pruebas.
- Implementación robusta para manejar desconexiones y paradas inesperadas.

### Archivos Generados:
- **eeg_data.csv**: Contiene las señales EEG con marcas de tiempo corregidas.
- **markers.csv**: Incluye los marcadores de eventos y sus marcas de tiempo sincronizadas.

