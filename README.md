# Student At-Risk Identification and Intervention Management System

## Run (Windows)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
python generate_data.py --students 100 --courses 10 --enrollments 200 --output data/generated
python validate_data.py --input data/generated
uvicorn backend.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

Frontend (second terminal):
```powershell
cd frontend
npm install
npm run dev
```
Full data: `python generate_data.py --students 5000 --courses 200 --enrollments 20000 --output data/generated`

Default seed: 20261022. Start small, then generate full volume. All records are synthetic.
Risk rules: attendance <75% +30; assessment average <50% +30; engagement decline +20; unresolved case +20. Unknown values add no points. These are illustrative rules, not validated academic thresholds.

The generator writes CSV and JSON exports, a data dictionary, manifest, and separate ground_truth.csv. Outcomes are generated from documented synthetic final-grade rules and must not be used as input features. This is a demonstration prototype, not production-ready student-record software; add authentication, authorization, audit/security review before real deployment.
