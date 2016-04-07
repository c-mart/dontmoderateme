See [https://dontmoderate.me](https://dontmoderate.me)

For development and testing, run PostgreSQL and Splash in containers:
- `docker run --name dmm-dev-postgres -e POSTGRES_USER=dmm-dev -e POSTGRES_PASSWORD=changeme123 -p 127.0.0.1:5432:5432 -d postgres:9.4`
- `docker run --name dmm-test-postgres -e POSTGRES_USER=dmm-test -e POSTGRES_PASSWORD=changeme123 -p 127.0.0.1:5433:5432 -d postgres:9.4`
- `docker run -p 5023:5023 -p 8050:8050 -p 8051:8051 -d scrapinghub/splash`

(In theory, we should be able to have just one container for both the development and test databases.) 