# Geospatial File Measurement API

A backend API built with **FastAPI** that accepts geospatial files in KML or Shapefile ZIP format, extracts their features, handles coordinate reference systems (CRS), calculates geometry measurements, and stores file metadata and measurement results in PostgreSQL.

## Features

* Upload `.kml` files
* Upload Shapefile packaged inside a `.zip`
* Validate uploaded file types
* Protect against oversized uploads
* Generate safe unique filenames for uploaded files
* Validate ZIP file paths to prevent unsafe extraction
* Extract geospatial features and properties
* Detect geometry types
* Read and preserve CRS information
* Transform geographic CRS to a suitable projected CRS before measurement
* Calculate:

  * Polygon / MultiPolygon area in square meters
  * LineString / MultiLineString length in meters
  * Point features without area or length measurement
* Store file metadata in PostgreSQL
* Store calculated measurements in PostgreSQL
* Provide REST APIs for file details and measurements
* Handle invalid and corrupted geospatial files
* Clean up temporary and processed uploaded files
* Automated API and validation tests with Pytest

## Tech Stack

* **Python**
* **FastAPI**
* **SQLAlchemy**
* **PostgreSQL**
* **GeoPandas**
* **Shapely**
* **PyProj**
* **Pytest**
* **Uvicorn**

## Project Architecture

```text
                         Client
                           |
                           v
                    +-------------+
                    |   FastAPI   |
                    +-------------+
                           |
                           v
                    +-------------+
                    | File Upload |
                    | Validation  |
                    +-------------+
                           |
                           v
                 +--------------------+
                 | Geospatial Service |
                 +--------------------+
                    |              |
                    v              v
                  KML        Shapefile ZIP
                    |              |
                    +-------+------+
                            |
                            v
                    +---------------+
                    |   GeoPandas   |
                    +---------------+
                            |
                            v
                    +---------------+
                    | CRS Handling  |
                    +---------------+
                            |
                            v
                    +-------------------+
                    | Measurement Logic |
                    +-------------------+
                      |       |       |
                      v       v       v
                    Area    Length   Point
                      |       |       |
                      +-------+-------+
                              |
                              v
                     +----------------+
                     |   PostgreSQL   |
                     +----------------+
                       |            |
                       v            v
                     files     measurements
```

## Project Structure

```text
geospatial-measurement-api/
│
├── app/
│   ├── __init__.py
│   │
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── files.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── init_db.py
│   │   └── models.py
│   │
│   └── services/
│       ├── __init__.py
│       └── geospatial_service.py
│
├── tests/
│   ├── conftest.py
│   ├── test_file_api.py
│   ├── test_geospatial_service.py
│   ├── test_measurement_api.py
│   └── ...
│
├── sample_data/
│   ├── test.kml
│   └── measurement_fixtures/
│
├── uploads/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Database Design

The application uses two main tables.

### `files`

Stores information about uploaded geospatial files.

| Column          | Description                  |
| --------------- | ---------------------------- |
| `id`            | Unique file ID               |
| `filename`      | Original uploaded filename   |
| `file_type`     | KML or ZIP                   |
| `crs`           | Coordinate Reference System  |
| `feature_count` | Number of extracted features |
| `status`        | Processing status            |
| `created_at`    | Upload timestamp             |

### `measurements`

Stores measurement results for individual features.

| Column             | Description                       |
| ------------------ | --------------------------------- |
| `id`               | Unique measurement ID             |
| `file_id`          | Related file                      |
| `feature_id`       | Feature index                     |
| `geometry_type`    | Point, LineString, Polygon, etc.  |
| `area`             | Area where applicable             |
| `length`           | Length where applicable           |
| `measurement_unit` | Measurement unit                  |
| `status`           | Measurement status                |
| `error_message`    | Error information when applicable |

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Nikita-238/geospatial-measurement-api.git
cd geospatial-measurement-api
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Create PostgreSQL database

Create a PostgreSQL database named:

```text
geospatial_measurement
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/geospatial_measurement
```

Do not commit the `.env` file to Git.

### 6. Create database tables

Run:

```powershell
python -m app.database.init_db
```

### 7. Start the application

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### 1. Upload a geospatial file

```http
POST /api/files/
```

Accepts:

* `.kml`
* `.zip` containing one Shapefile

Example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/api/files/" \
  -F "file=@sample_data/test.kml"
```

Example response:

```json
{
  "id": 1,
  "filename": "test.kml",
  "file_type": "kml",
  "crs": "EPSG:4326",
  "feature_count": 1,
  "status": "processed"
}
```

### 2. Get file details

```http
GET /api/files/{file_id}/
```

Example:

```text
GET /api/files/1/
```

Returns information about the uploaded file, including its CRS, feature count, and processing status.

### 3. Get measurements

```http
GET /api/files/{file_id}/measurements/
```

Example:

```text
GET /api/files/1/measurements/
```

Example response:

```json
[
  {
    "feature_id": 0,
    "geometry_type": "Polygon",
    "area": 11579.699250237536,
    "length": null,
    "measurement_unit": "square_meters",
    "status": "success"
  }
]
```

## Measurement Logic

The measurement calculation depends on the geometry type.

| Geometry        | Measurement    |
| --------------- | -------------- |
| Polygon         | Area           |
| MultiPolygon    | Area           |
| LineString      | Length         |
| MultiLineString | Length         |
| Point           | No measurement |

### Polygon

For polygons, the API calculates:

```text
area = geometry.area
```

The result is stored in square meters.

### LineString

For lines, the API calculates:

```text
length = geometry.length
```

The result is stored in meters.

### Point

Points do not have area or length, so both measurement values remain `null`.

## CRS Handling

Accurate geospatial measurements cannot be calculated directly from geographic coordinates such as latitude and longitude because those coordinates are expressed in degrees rather than linear distance units.

The application therefore checks the input CRS before calculating measurements.

### Projected CRS

If the input data already uses a projected CRS, that CRS is used for measurement.

### Geographic CRS

If the input data uses a geographic CRS such as:

```text
EPSG:4326
```

the application estimates a suitable projected CRS using GeoPandas and transforms the data before calculating measurements.

This avoids calculating area or distance directly from latitude/longitude values.

### Missing CRS

If the input file does not contain CRS information, the API rejects the measurement operation because an accurate measurement cannot be guaranteed.

## File Validation and Security

The application includes several validation and security measures.

### File type validation

Only the following extensions are accepted:

```text
.kml
.zip
```

### File size validation

Uploads are limited to:

```text
10 MB
```

### Safe ZIP extraction

ZIP member paths are validated before extraction to prevent unsafe paths such as:

```text
../../some_file
```

### Single Shapefile requirement

A ZIP file must contain exactly one `.shp` file.

ZIP files containing:

* no Shapefile
* multiple Shapefiles
* corrupted ZIP data

are rejected.

### Temporary file cleanup

Uploaded files are removed after successful processing.

Temporary Shapefile extraction directories are automatically removed after processing.

Failed processing also triggers cleanup.

## Error Handling

The API returns appropriate HTTP responses for common failures.

| Situation                        | Status |
| -------------------------------- | -----: |
| Unsupported file extension       |  `400` |
| Invalid/corrupted KML            |  `400` |
| Invalid/corrupted ZIP            |  `400` |
| Invalid Shapefile                |  `400` |
| Missing CRS                      |  `400` |
| Unsafe ZIP path                  |  `400` |
| File larger than 10 MB           |  `413` |
| File not found                   |  `404` |
| Unexpected server/database error |  `500` |

Internal exception details are not exposed for unexpected server errors.

## Testing

The project uses **Pytest** for automated testing.

Run the complete test suite:

```powershell
python -m pytest -v
```

The tests cover:

* Health endpoint
* Invalid file extension
* File not found
* Measurement endpoint validation
* KML upload
* Polygon measurement
* LineString measurement
* Point handling
* Missing CRS
* Corrupted KML
* Corrupted ZIP
* Invalid Shapefile
* Multiple Shapefiles in ZIP
* Missing Shapefile in ZIP
* Unsafe ZIP paths
* File size validation
* Uploaded file cleanup
* Test database isolation

## Design Decisions

### Why FastAPI?

FastAPI provides:

* Simple REST API development
* Automatic OpenAPI documentation
* Request validation
* Good support for Python-based backend services

### Why GeoPandas?

GeoPandas provides convenient support for reading and processing geospatial vector data and works well with Shapely and PyProj.

### Why Shapely?

Shapely provides geometry operations such as area and length calculations.

### Why PyProj?

PyProj is used for CRS handling and coordinate transformation.

### Why PostgreSQL?

PostgreSQL provides reliable relational storage for file metadata and measurement results.

The current MVP does not require PostGIS because the geospatial calculations are performed in the application layer using GeoPandas, Shapely, and PyProj.

PostGIS can be considered as a future enhancement for more advanced spatial queries and large-scale geospatial workloads.

### Why temporary extraction?

Shapefiles consist of multiple related files such as `.shp`, `.shx`, `.dbf`, and `.prj`. Temporary extraction allows the complete Shapefile package to be processed together while avoiding unnecessary permanent storage.

## Learning

While building this project, I worked with:

* FastAPI REST API development
* PostgreSQL database integration
* SQLAlchemy ORM
* GeoPandas
* Shapely geometry operations
* CRS and coordinate transformations
* KML and Shapefile processing
* File validation
* ZIP security
* Automated testing with Pytest
* Error handling and cleanup
* Git-based development workflow

## Future Scope

Possible improvements include:

* PostGIS integration
* Docker and Docker Compose
* Background processing for large files
* Redis/Celery-based job processing
* Authentication and authorization
* Support for additional formats such as GeoJSON and GeoPackage
* Pagination for large feature collections
* Spatial filtering and querying
* Cloud object storage
* API rate limiting
* More detailed processing logs
* Frontend interface for file upload and visualization

## Current Scope

This project focuses on the backend MVP required for geospatial file processing and measurement.

It intentionally keeps the architecture simple while maintaining clear separation between:

```text
API layer
    ↓
Geospatial processing layer
    ↓
Database layer
```

This makes the application easier to test and provides a foundation for future production enhancements.

## Author

**Nikita Magar**

B.Tech Electronics & Computer Engineering
Sanjivani College of Engineering, Kopargaon
