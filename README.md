# Instalily AI Case Study - PartSelect Chat Agent

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Overview
This project implements a focused, production style chat agent for the PartSelect e-commerce experience, limited to refrigerator and dishwasher parts.

The agent helps users:
- find parts
- check compatibility with appliance models
- find installation guides
- troubleshoot common appliance issues
- get basic support regarding orders

My focus for this project was correctness, clarity, and extensibility thus the need to maintain a small set of seeded data and follow deterministic workflows.


## Architecture Summary

The system uses a deterministic agent core with LLM augmentation for language quality.


```
React (CRA) Frontend
        |
FastAPI Backend
        |
        +-- Intent Detection (rules)
        +-- Scope Guard (hard limits)
        +-- Deterministic Knowledge
        |     - Parts seed
        |     - Compatibility table
        |     - Installation guides
        |     - Troubleshooting flows
        |
        +-- LLM (optional, using Gemini)
              - Rewrite responses for clarity
              - Fallback clarifying question only
```

### Reasons for this design
- the deterministic nature means that the agent will stick to the facts and made debugging easier
- the LLM is secondary so that the user experience can be improved without compromising the facts
- every answer can be traced back to a data source (using seeds as of now)


## Frontend

The framework used is the Create React App from the provided template.\
Key features:
- Chat user interface with message history
- The production cards (product images and descriptions) are rendered inline
- There are 2 actions buttons for installation and compatibility checks and a redirect link to the PartSelect website

## Backend

I used the FastAPI framework and Python 3.11 for the backend.\
For the sake of simplicity and explicity, I used in-memory per session to preserve state. \

### Core Components

#### 1. Intent Detection
The intent detection is rule based and classifies the user input into one of:
- INSTALL
- COMPATIBILITY
- TROUBLESHOOT
- FIND_PART
- ORDER_SUPPORT
- OTHER_IN_SCOPE

#### 2. Scope Guard
Following the prompt, the agent is strictly limited to:
- refrigerators
- dishwashers
- PartSelect style parts

Out-of-scope requests receive a polite redirect to ensure the agent does not wander.

#### 3. Seeded Knowledge
All authoritative data is local and inspectable to try and mirror the internal databases:

| Data Type              | File Path                                   |
|------------------------|----------------------------------------------|
| Parts                  | `backend/data/parts_seed.json`               |
| Compatibility          | `backend/data/compatibility.csv`             |
| Installation guides    | `backend/data/guides_seed.json`              |
| Troubleshooting flows  | `backend/data/troubleshoot_seed.json`        |


#### 4. Troubleshooting Engine

Troubleshooting is implemented as a **guided decision tree** designed to minimize user overload and avoid premature upselling.

**Flow:**
- **Trigger phrase - topic**
- Ask **one question at a time**
- Store user answers in **session memory**
- **Dynamically tailor** the checklist order based on responses
- Show **likely replacement parts only after diagnosis**

**Example Topics:**
- Dishwasher grinding noise
- Refrigerator ice maker not working
- Refrigerator buzzing or humming

This approach keeps the experience focused, reduces cognitive load, and ensures that part recommendations are grounded in an actual diagnosis rather than assumptions.




## LLM Integration (Gemini)

### Why I Used an LLM

The LLM does not decide the facts but is onlu used to:

- Rewrite already-generated responses for clarity and friendliness
- Ask one clarifying question when deterministic logic cannot proceed

All factual decisions, diagnostics, and recommendations remain fully deterministic.

---

### Gemini Setup

The project uses **Gemini Flash**, configured via an environment variable:

```bash
export GEMINI_API_KEY="your_key_here"
```

This ensures the LLM remains a lightweight, optional layer focused strictly on language quality and conversational flow.

### Fallback Behavior (No API Key)

If no Gemini API key is set the system continues working normally and deterministic responses are used exclusively.\

This guarantees full operation without any dependency on an external LLM service.

## Safety Rules

The LLM is explicitly instructed to:

- **Not invent parts**
- **Not invent compatibility**
- **Not invent prices**
- **Not invent instructions**

All factual content must originate from the system’s deterministic data sources and logic (seed).

---

## Running the Project

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Health check
```bash
curl http://localhost:8000/health
```

### Frontend
```bash
npm install
npm start
```

App runs at:
```bash
http://localhost:3000
```


## Example Supported Flows

### Installation

**User:** “How do I install PS11752778?”

- Stepwise guide  
- Tools and safety notes  
- Product card  

---

### Compatibility

**User:** “Is PS11752778 compatible with WDT780SAEM1?”

- Deterministic yes/no  
- Source citation  
- Product card  

---

### Troubleshooting

**User:** “My dishwasher is making a grinding noise”

- Guided questions  
- Tailored checklist  
- Suggested replacement parts  

---

## Extensibility


### Possible Extensions

- Replace seeds with real PartSelect APIs  
- Persist sessions 
- Add order lookup integration  
- Expand appliance categories  
- Add embeddings for fuzzy troubleshooting matches  



## Author
Maxwell Onyango
Instalily AI Take Home Case Study