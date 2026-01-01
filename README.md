# Recipe App API

A robust REST API for managing recipes, built with Django, Django REST Framework, and Docker.

## 🚀 Features

- **User Authentication**: Create users and manage authentication tokens.
- **Recipe Management**: Create, read, update, and delete recipes.
- **Tag & Ingredient Management**: Organize recipes with tags and ingredients.
- **Image Upload**: Support for uploading recipe images.
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation.

## 🛠 Technologies

- **Python 3.9+**
- **Django 3.2+**
- **Django REST Framework**
- **PostgreSQL**
- **Docker & Docker Compose**
- **drf-spectacular** (for API schema generation)

## 📂 Project Structure

The project is organized into modular apps:

- **`core`**: Core functionality, database models, and management commands.
- **`user`**: User creation and authentication logic.
- **`recipe`**: Logic for recipes, tags, and ingredients.

## 🔧 Installation & Running

This project uses Docker for easy setup and execution.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd recipe-app
    ```

2.  **Build and run the project:**
    ```bash
    docker compose up --build
    ```

    This command will:
    - Build the Docker image.
    - Start the PostgreSQL database.
    - Run migrations (`wait_for_db`, `makemigrations`, `migrate`).
    - Start the development server on port `8000`.

3.  **Access the API:**
    Open your browser and navigate to: http://localhost:8000/api/docs/

## 📖 API Documentation

The API documentation is automatically generated using `drf-spectacular`.

- **Swagger UI**: http://localhost:8000/api/docs/
- **Schema Download**: http://localhost:8000/api/schema/

## 🧪 Running Tests

To run the test suite inside the Docker container:

```bash
docker compose run --rm app sh -c "python manage.py test"
```

## 👤 Author

Developed by Maria Victoria Perez Contrera
