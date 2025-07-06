# 🔧 Async Job Processor API – FastAPI, Celery, Redis, PostgreSQL

This is a scalable, containerized backend service built using **FastAPI** with async support, **Celery** for background task processing, **Redis** as the message broker, and **PostgreSQL** as the database.

### 🚀 Features

- Submit a job to compute the `square_sum` or `cube_sum` of a list of numbers
- Asynchronous job processing using Celery
- Polling job status and result
- PostgreSQL as the persistent store
- Redis as the Celery broker
- Fully containerized using Docker Compose

---

## 🏗️ Architecture Overview

```
Client → FastAPI (async API)
       → PostgreSQL (store jobs)
       → Redis (task queue)
       → Celery Worker (process jobs in background)
```

---

## 📦 Tech Stack

| Layer         | Technology              |
|---------------|--------------------------|
| API Framework | FastAPI (Python 3.10)    |
| Task Queue    | Celery                   |
| Message Broker| Redis                    |
| Database      | PostgreSQL + SQLAlchemy  |
| Containerization | Docker + Docker Compose |
| Async Support | Yes (`async def` endpoints, background job queue) |

---

## ⚙️ API Endpoints

### 1. **Submit a Job**
```
POST /jobs/
```

#### Request:
```json
{
  "data": [1, 2, 3],
  "operation": "square_sum" // or "cube_sum"
}
```

#### Response:
```json
{
  "job_id": "<uuid>",
  "status": "PENDING"
}
```

---

### 2. **Check Job Status**
```
GET /jobs/{job_id}/status
```

#### Response:
```json
{
  "status": "IN_PROGRESS"
}
```

---

### 3. **Get Job Result**
```
GET /jobs/{job_id}/result
```

#### Response:
```json
{
  "job_id": "<uuid>",
  "status": "SUCCESS",
  "result": 14.0
}
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Environment Setup

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres@db:6543/job_db
REDIS_URL=redis://redis:6379/0
```

---

### 3. Build and Run the App

```bash
docker-compose up --build
```

This will:
- Launch FastAPI on `http://localhost:8000`
- Run Redis and PostgreSQL containers

---

### 4. Start Celery Worker

In another terminal:

```bash
docker-compose exec api celery -A app.tasks worker --loglevel=info
```

---

### 5. Open API Docs

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

Use Swagger UI to:
- Submit jobs
- Check status
- Get results

---

## 🧠 Async Architecture Explained

- API routes use `async def` for async compatibility
- Long-running jobs (e.g., sum of cubes) are **offloaded to Celery**
- This prevents blocking the API server
- Celery workers poll Redis for tasks and update results in PostgreSQL

---

## 🐳 Docker Services

| Service | Port | Description               |
|---------|------|---------------------------|
| FastAPI | 8000 | Backend API server        |
| Redis   | 6379 | Celery broker             |
| Postgres| 5432 | Data storage              |

---

## 🧪 Example Curl Commands

Submit a job:
```bash
curl -X POST http://localhost:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d '{"data": [2, 3], "operation": "cube_sum"}'
```

Check status:
```bash
curl http://localhost:8000/jobs/<job_id>/status
```

Get result:
```bash
curl http://localhost:8000/jobs/<job_id>/result
```

---

## 🛠 Troubleshooting

- If you see `SSL SYSCALL error: EOF detected`, ensure:
  - `DATABASE_URL` doesn’t include `?sslmode=require`
  - Use `pool_pre_ping=True` in SQLAlchemy engine
  - Restart Celery if DB restarts

---

## 📚 Future Enhancements (Optional)

- JWT Authentication
- Job expiry / cleanup
- Pagination for job list
- Async SQLAlchemy with `asyncpg`
- Retry logic for failed tasks

---

## 🧑‍💻 Author

**Ravikant Tiwari**  
Backend Developer | IIIT Kalyani 2024  
💼 [LinkedIn](https://linkedin.com/in/ravikant-tiwari)  
🧠 GitHub: [github.com/ravikanttiwari](https://github.com/ravikanttiwari)

---

## ✅ Status

✔️ Assignment Complete  
✔️ Production-ready architecture  
✔️ Async API with background job processing  
