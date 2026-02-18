# Hack_oncology

Система управления клиническими исследованиями в онкологии / Oncology Clinical Trial Management System

## Описание проекта / Project Description

Это комплексная система для планирования и управления клиническими исследованиями противоопухолевых препаратов. Система включает модули для работы с фармакокинетическими данными, выбора дизайна исследования, расчета размера выборки, регуляторных проверок и генерации синопсиса протокола исследования.

This is a comprehensive system for planning and managing clinical trials of oncology drugs. The system includes modules for working with pharmacokinetic data, study design selection, sample size calculation, regulatory checks, and protocol synopsis generation.

## Структура проекта / Project Structure

```
.
├── config.py                      # Константы, пути, базовые настройки / Constants, paths, basic settings
├── models/
│   └── domain.py                  # Доменные сущности / Domain entities (Drug, PK parameters, Study design)
├── pk_data/
│   └── source_pubmed.py           # Модуль для получения PK-данных / Module for retrieving PK data
├── design/
│   └── logic.py                   # Выбор дизайна исследования / Study design selection logic
├── stats/
│   └── sample_size.py             # Расчёт размера выборки / Sample size calculation
├── reg/
│   └── checks.py                  # Регуляторные проверки / Regulatory compliance checks
├── synopsis/
│   ├── templates.py               # Шаблоны текстовых блоков / Text block templates
│   └── generator.py               # Сборка синопсиса / Synopsis assembly
├── api/
│   └── main.py                    # FastAPI endpoints
├── demo/
│   └── example_workflow.py        # End-to-end демонстрация / End-to-end demo script
└── requirements.txt               # Python зависимости / Python dependencies
```

## Установка / Installation

1. Клонируйте репозиторий / Clone the repository:
```bash
git clone https://github.com/FuturumHumanitatis/Hack_oncology.git
cd Hack_oncology
```

2. Установите зависимости / Install dependencies:
```bash
pip install -r requirements.txt
```

## Использование / Usage

### Запуск демонстрационного workflow / Running the demo workflow

```bash
PYTHONPATH=. python3 demo/example_workflow.py
```

Этот скрипт демонстрирует полный цикл работы с системой:
1. Определение исследуемого препарата
2. Получение PK-данных
3. Выбор дизайна исследования
4. Расчет размера выборки
5. Определение популяции и конечных точек
6. Регуляторные проверки
7. Генерация синопсиса

This script demonstrates the complete system workflow:
1. Drug definition
2. PK data retrieval
3. Study design selection
4. Sample size calculation
5. Population and endpoints definition
6. Regulatory compliance checks
7. Synopsis generation

### Запуск API сервера / Running the API server

```bash
PYTHONPATH=. python3 api/main.py
```

API будет доступен по адресу / API will be available at: http://localhost:8000

Документация API / API documentation: http://localhost:8000/docs

### Доступные API endpoints / Available API endpoints

- `GET /` - Информация о API / API information
- `POST /pk-data` - Получение PK-данных / Retrieve PK data
- `POST /design/recommend` - Рекомендация дизайна исследования / Recommend study design
- `POST /sample-size/calculate` - Расчет размера выборки / Calculate sample size
- `POST /regulatory/check` - Проверка регуляторных требований / Check regulatory compliance
- `POST /synopsis/generate` - Генерация синопсиса / Generate synopsis
- `GET /health` - Проверка работоспособности / Health check

## Модули системы / System Modules

### config.py
Содержит константы и настройки:
- Пути к директориям
- Настройки API
- Статистические параметры по умолчанию
- Регуляторные настройки

Contains constants and settings:
- Directory paths
- API settings
- Default statistical parameters
- Regulatory settings

### models/domain.py
Доменные сущности системы:
- `Drug` - препарат
- `PKParameter` - фармакокинетический параметр
- `PKProfile` - полный PK-профиль
- `StudyDesign` - дизайн исследования
- `StudyPopulation` - популяция исследования
- `Endpoint` - конечная точка
- `ClinicalStudy` - клиническое исследование

Domain entities:
- `Drug` - pharmaceutical compound
- `PKParameter` - pharmacokinetic parameter
- `PKProfile` - complete PK profile
- `StudyDesign` - study design
- `StudyPopulation` - study population
- `Endpoint` - study endpoint
- `ClinicalStudy` - clinical study

### pk_data/source_pubmed.py
Модуль для получения фармакокинетических данных из PubMed (заглушка с тестовыми данными).

Module for retrieving pharmacokinetic data from PubMed (stub with mock data).

### design/logic.py
Логика выбора дизайна исследования:
- Рекомендации на основе характеристик препарата
- Валидация дизайна
- Сравнение типов дизайна

Study design selection logic:
- Recommendations based on drug characteristics
- Design validation
- Design type comparison

### stats/sample_size.py
Расчет размера выборки для различных дизайнов:
- Параллельный дизайн
- Перекрестный дизайн
- Исследования биоэквивалентности
- Анализ чувствительности

Sample size calculation for different designs:
- Parallel design
- Crossover design
- Bioequivalence studies
- Sensitivity analysis

### reg/checks.py
Проверка соответствия регуляторным требованиям:
- Валидация протокола
- Проверка GCP-соответствия
- Генерация регуляторного чек-листа

Regulatory compliance checks:
- Protocol validation
- GCP compliance checking
- Regulatory checklist generation

### synopsis/templates.py
Шаблоны для генерации разделов синопсиса:
- Титульная страница
- Обоснование
- Цели исследования
- Дизайн исследования
- Популяция
- Статистический анализ
- Регуляторные аспекты

Templates for synopsis section generation:
- Title page
- Background and rationale
- Study objectives
- Study design
- Population
- Statistical analysis
- Regulatory considerations

### synopsis/generator.py
Генератор синопсиса протокола исследования:
- Сборка полного синопсиса
- Генерация отдельных разделов
- Экспорт в файл

Study protocol synopsis generator:
- Full synopsis assembly
- Individual section generation
- File export

### api/main.py
FastAPI приложение с REST API endpoints для всех функций системы.

FastAPI application with REST API endpoints for all system functions.

## Пример использования / Usage Example

```python
from models.domain import Drug
from pk_data.source_pubmed import get_pk_data_source
from design.logic import get_design_selector
from stats.sample_size import get_sample_size_calculator

# Определение препарата
drug = Drug(
    name="Test Drug",
    active_ingredient="Compound-X",
    indication="NSCLC",
    dosage_form="Tablet",
    route_of_administration="Oral"
)

# Получение PK-данных
pk_source = get_pk_data_source()
pk_profile = pk_source.search_pk_data(drug)

# Выбор дизайна
design_selector = get_design_selector()
design = design_selector.recommend_design(drug, pk_profile)

# Расчет размера выборки
calculator = get_sample_size_calculator()
sample_size = calculator.calculate_parallel_design(
    effect_size=300.0,
    std_dev=500.0
)
```

## Технологии / Technologies

- Python 3.8+
- FastAPI - веб-фреймворк / web framework
- Pydantic - валидация данных / data validation
- SciPy - статистические расчеты / statistical calculations

## Лицензия / License

MIT

## Контрибьюторы / Contributors

FuturumHumanitatis