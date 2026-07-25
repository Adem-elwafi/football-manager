# Football Match Manager

Weekly football match organizer with attendance, payment tracking, expense management, and team generation.

## Architecture

```
app.py                    Entry point
db/                       Database layer (connection, schema)
models/                   Dataclass definitions
repositories/             Data access (SQL → model mapping)
services/                 Business logic layer
ui/                       Streamlit presentation layer
utils/                    Pure helper functions
```

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Development

Each phase produces a Definition of Done report. See ADRs in the plan document for architectural decisions.
