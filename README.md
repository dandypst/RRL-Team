# RRL-Team Dashboard

Dashboard monitoring untuk RRL-Team Multi-Agent System.

## 🚀 Deployed on Streamlit Cloud

**Live URL:** (akan tersedia setelah deploy)

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Edit `config/agents.yaml` untuk menambah/mengubah agent monitoring.

## Secrets

Untuk Streamlit Cloud, tambahkan secrets di dashboard:
- `DASHBOARD_PASSWORD` — password login

## Default Login
- Username: `admin`
- Password: (set via secrets atau default: `password`)
