# FitApp - Gestione Allenamenti Coach/Allievi

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Descrizione

FitApp è un'applicazione per la gestione di schede di allenamento tra coach e allievi. Permette:
- **Registrazione** come coach o allievo
- **Coach**: creano e gestiscono schede di allenamento
- **Allievi**: seguono le schede assegnate dal proprio coach

## Funzionalità principali
- **Autenticazione** JWT sicura
- **Dashboard separata** per coach e allievi
- **Gestione completa** delle schede di allenamento
- **Assegnazione** di esercizi agli allievi
- **Monitoraggio** dei progressi

## Tecnologie
- **Backend**: FastAPI (Python)
- **Database**: SQLite (con SQLAlchemy ORM)
- **Autenticazione**: OAuth2 con JWT
- **Validazione dati**: Pydantic 2.0

## Installazione

### Prerequisiti
- Python 3.9+
- Pip

### Passi per l'installazione
1. Clonare il repository:
   ```bash
   git clone https://github.com/tuo-username/fitapp.git
   cd fitapp
