## Lexicon

---
**About Lexixon Word** : [About Lexicon Word](https://en.wikipedia.org/wiki/Lexicon)
---

**Lexicon** is an advanced application that integrates language processing with video content, enabling a seamless combination of subtitles with video playback. The primary functionality of Lexicon allows users to upload videos, after which the backend processes these files to extract subtitles and store them in a database. When the video is played, the corresponding subtitles are integrated with the video, providing a synchronized playback experience.

Key features of Lexicon include:
1. **Video Upload & Subtitle Extraction**: Users can upload videos, and the system automatically extracts and saves subtitles.
2. **Subtitle Integration**: Subtitles are synchronized with video playback, providing optional caption toggling (on/off).
3. **Video Controls**: Full video control features such as play, pause, forward, rewind, and volume control.
4. **Search Functionality**: Users can search for specific phrases within the subtitles. The system shows where these phrases appear in the video with their timestamps, allowing users to jump directly to the relevant section of the video.

This application supports multiple languages and is designed to enhance accessibility and interaction with video content.

---

## Requirements

Before setting up Lexicon, ensure you have the following software and versions installed:

1. **Python** (v3.8+)
2. **FFmpeg** (v4.2.7) — For video and subtitle processing.
3. **Poetry** (v1.3+) — For dependency management and packaging.
4. **Virtualenv** (v20.25+) — For creating isolated Python environments.
5. **PostgreSQL** (v14.X+) — For database management.
6. **Redis** (v4.3+) — For task queuing and caching.

---

## Services Stack for development :

To ease a local development, in the project root directory, we have docker compose based `docker-compose.stack.yml` 
file. All required services we need for running this project like postgres, redis etc. have mentioned in it.
You should also install [docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) in your machine and setup them.

Go to the project root directory, and simply run following command to up and down stack services.

* To start all services in background

    ```bash
    docker-compose -f docker-compose.stack.yml up -d
    ```

* To shutdown all running services

    ```bash
    docker-compose -f docker-compose.stack.yml down
    ```

## Setting Up PostgreSQL Database

Follow these steps to configure your PostgreSQL database:

1. **Log in to the PostgreSQL shell**:

    ```bash
    sudo -u postgres psql
    ```

2. **Create a new database and user**:

    ```sql
    CREATE DATABASE lexicon_db;
    CREATE USER lexicon_user WITH PASSWORD 'your_secure_password';
    GRANT ALL PRIVILEGES ON DATABASE lexicon_db TO lexicon_user;
    ```

Replace `lexicon_db`, `lexicon_user`, and `'your_secure_password'` with your desired database name, user name, and a secure password.

---

## Managing Virtual Environment

You can use **virtualenv**, **Poetry**, or **pyenv** to manage your virtual environment. Below are the instructions using `virtualenv`:

1. **Create a virtual environment** in the root directory of the project:

    ```bash
    virtualenv --python=python3.8 .venv
    ```

2. **Activate the virtual environment**:

    ```bash
    source .venv/bin/activate
    ```

3. **Deactivate the virtual environment** when done:

    ```bash
    deactivate
    ```

---

## Installation Instructions

### 1. Install Project Dependencies

Ensure your virtual environment is activated. Install the necessary project dependencies using `Poetry`:

```bash
poetry install
```

### 2. Configure Environment Variables

Copy the example environment file and set up specific configurations for your environment:

```bash
cp .env.example .env.development
```

You may create other configurations as needed, such as:
- `.env.staging` for the staging environment.
- `.env.production` for the production environment.

Edit the environment file to include your PostgreSQL database credentials and other sensitive data.

### 3. Apply Database Migrations

Run the following command to apply the initial database migrations:

```bash
python manage.py migrate
```

### 4. Collect Static Files

To ensure all static files are collected and prepared for deployment, run:

```bash
python manage.py collectstatic
```

### 5. Run the Application

To run the development server locally with automatic reload, execute:

```bash
python manage.py runserver
```

You can now access the application at:

```bash
http://localhost:8000/
```

---

## Accessing the Application

### 1. **Login Page**:

Visit the login page to authenticate (if authentication is enabled):

```bash
http://localhost:8000/login/
```

### 2. **Video List Page**:

To view the list of uploaded videos, go to:

```bash
http://localhost:8000/list/
```

_Note: Currently, video listing is publicly accessible without authentication._

---

## Additional Configuration (Optional)

### Using Redis

Redis is required for task management and queuing (e.g., for background processing of video uploads and subtitle extraction). To start Redis, install it based on your operating system’s package manager. On Ubuntu, for example:

```bash
sudo apt-get install redis-server
```

Ensure Redis is running with:

```bash
sudo systemctl start redis
```

### Setting Up Celery for Background Tasks

Celery is used to handle asynchronous tasks, such as processing video uploads and subtitle extraction. To run Celery, execute the following command:

```bash
celery -A lexicon worker -l info
```

---

## Useful Links

Here are some useful links to help you set up dependencies and tools:

1. **FFmpeg**: [Download FFmpeg](https://www.ffmpeg.org/download.html)
2. **Poetry**: [Poetry Documentation](https://python-poetry.org/docs/)
3. **PostgreSQL**: [PostgreSQL Installation Guide](https://www.devart.com/dbforge/postgresql/how-to-install-postgresql-on-linux/)
4. **Redis**: [Redis Documentation](https://redis.io/documentation)
5. **Celery**: [Celery Documentation](https://docs.celeryq.dev/en/stable/)

---

## Issues

Please create an issue if you find any difficulties setting up or running the project. [Raise Issue](https://github.com/bytesbit/lexicon/issues/new).

Let me know if you'd like further adjustments!
