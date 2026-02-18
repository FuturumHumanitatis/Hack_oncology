# Quick Start Guide / Руководство по быстрому старту

## Быстрый старт / Quick Start

### 1. Установка / Installation

```bash
# Клонирование репозитория / Clone repository
git clone https://github.com/FuturumHumanitatis/Hack_oncology.git
cd Hack_oncology

# Установка зависимостей / Install dependencies
pip install -r requirements.txt
```

### 2. Запуск демо / Run Demo

```bash
# Запустить демонстрационный workflow
# Run demo workflow
PYTHONPATH=. python3 demo/example_workflow.py
```

Этот скрипт создаст полный пример клинического исследования и сгенерирует синопсис в `/tmp/`.

This script will create a complete clinical trial example and generate a synopsis in `/tmp/`.

### 3. Запуск API / Run API

```bash
# Запустить FastAPI сервер
# Start FastAPI server
PYTHONPATH=. python3 api/main.py
```

Откройте браузер / Open browser: http://localhost:8000/docs

### 4. Основные примеры использования / Basic Usage Examples

#### Пример 1: Получение PK-данных / Example 1: Get PK Data

```python
from models.domain import Drug
from pk_data.source_pubmed import get_pk_data_source

# Создание объекта препарата
drug = Drug(
    name="MyDrug",
    active_ingredient="Active-X",
    indication="Cancer",
    dosage_form="Tablet",
    route_of_administration="Oral"
)

# Получение PK-данных
pk_source = get_pk_data_source()
pk_profile = pk_source.search_pk_data(drug)

# Вывод параметров
for param in pk_profile.parameters:
    print(f"{param.parameter_name}: {param.value} {param.unit}")
```

#### Пример 2: Выбор дизайна исследования / Example 2: Select Study Design

```python
from design.logic import get_design_selector

# Получение рекомендации по дизайну
design_selector = get_design_selector()
design = design_selector.recommend_design(
    drug=drug,
    pk_profile=pk_profile,
    number_of_treatments=2
)

print(f"Recommended design: {design.design_type}")
print(f"Treatment duration: {design.treatment_duration} days")
```

#### Пример 3: Расчет размера выборки / Example 3: Calculate Sample Size

```python
from stats.sample_size import get_sample_size_calculator

calculator = get_sample_size_calculator()

# Для параллельного дизайна
result = calculator.calculate_parallel_design(
    effect_size=300.0,
    std_dev=500.0,
    number_of_arms=2
)

print(f"Sample size per group: {result['adjusted_n_per_group']}")
print(f"Total sample size: {result['adjusted_total_n']}")
```

#### Пример 4: Регуляторные проверки / Example 4: Regulatory Checks

```python
from models.domain import ClinicalStudy, StudyDesign, Endpoint
from reg.checks import get_regulatory_checker

# Создание исследования
study = ClinicalStudy(
    study_id="STUDY-001",
    title="Phase II Study",
    drug=drug,
    design=design,
    sample_size=50
)

# Добавление конечной точки
study.endpoints.append(Endpoint(
    name="Overall Response Rate",
    endpoint_type="primary",
    description="ORR"
))

# Проверка соответствия
checker = get_regulatory_checker("FDA")
violations = checker.check_study_compliance(study)

print(f"Violations found: {len(violations)}")
for v in violations:
    print(f"- [{v.severity}] {v.description}")
```

#### Пример 5: Генерация синопсиса / Example 5: Generate Synopsis

```python
from synopsis.generator import get_synopsis_generator

generator = get_synopsis_generator()

# Генерация полного синопсиса
synopsis = generator.generate_full_synopsis(
    study=study,
    sample_size_result=result,
    regulatory_body="FDA"
)

print(synopsis)

# Сохранение в файл
generator.export_to_file(
    study=study,
    filename="synopsis.txt",
    sample_size_result=result
)
```

### 5. API Примеры / API Examples

#### Получение PK-данных / Get PK Data

```bash
curl -X POST "http://localhost:8000/pk-data" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TestDrug",
    "active_ingredient": "Compound-X",
    "indication": "Cancer",
    "dosage_form": "Tablet",
    "route_of_administration": "Oral"
  }'
```

#### Рекомендация дизайна / Recommend Design

```bash
curl -X POST "http://localhost:8000/design/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "drug": {
      "name": "TestDrug",
      "active_ingredient": "Compound-X",
      "indication": "Cancer",
      "dosage_form": "Tablet",
      "route_of_administration": "Oral"
    },
    "design_params": {
      "number_of_treatments": 2
    }
  }'
```

#### Расчет размера выборки / Calculate Sample Size

```bash
curl -X POST "http://localhost:8000/sample-size/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "design_type": "parallel",
    "effect_size": 300.0,
    "std_dev": 500.0,
    "number_of_arms": 2
  }'
```

## Структура проекта / Project Structure

```
Hack_oncology/
├── config.py              # Конфигурация / Configuration
├── models/                # Модели данных / Data models
├── pk_data/              # PK данные / PK data
├── design/               # Дизайн исследования / Study design
├── stats/                # Статистика / Statistics
├── reg/                  # Регуляторика / Regulatory
├── synopsis/             # Синопсис / Synopsis
├── api/                  # API endpoints
└── demo/                 # Демо скрипты / Demo scripts
```

## Документация модулей / Module Documentation

### config.py
- Константы и настройки системы
- System constants and settings

### models/domain.py
- `Drug` - Препарат / Drug entity
- `PKProfile` - PK профиль / PK profile
- `StudyDesign` - Дизайн / Study design
- `ClinicalStudy` - Исследование / Clinical study

### pk_data/source_pubmed.py
- Получение PK-данных из PubMed
- Retrieve PK data from PubMed

### design/logic.py
- Выбор и валидация дизайна исследования
- Study design selection and validation

### stats/sample_size.py
- Расчет размера выборки
- Sample size calculation

### reg/checks.py
- Регуляторные проверки
- Regulatory compliance checks

### synopsis/templates.py & generator.py
- Генерация синопсиса протокола
- Protocol synopsis generation

### api/main.py
- FastAPI REST API endpoints

## Поддержка / Support

Для вопросов и предложений создавайте issues на GitHub.

For questions and suggestions, create issues on GitHub.

## Лицензия / License

MIT
