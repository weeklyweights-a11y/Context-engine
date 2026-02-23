# Docker Commands for Phase 4

## Rebuild and run (after code changes)

```bash
cd Hackathon
docker compose build --no-cache
docker compose up -d
```

## Rebuild only when adding new npm deps (e.g. recharts)

```bash
docker compose build --no-cache frontend
docker compose up -d
```

## Run backend tests inside Docker

```bash
docker compose exec backend pytest app/tests -v
```

## Run Phase 4 tests only

```bash
docker compose exec backend pytest app/tests/test_search_service.py app/tests/test_similar.py app/tests/test_customer_profile.py app/tests/test_search_routes.py -v
```

## View logs

```bash
docker compose logs -f backend
docker compose logs -f frontend
```
