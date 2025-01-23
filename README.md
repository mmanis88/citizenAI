# CitizenAI

CitizenAI is a FastAPI-based application designed to handle queries and provide responses with inline clickable citations. The application uses FAISS for efficient search, integrates OpenAI's GPT models for generating summaries, and employs modern CI/CD practices for robust development and deployment workflows.

---

## Table of Contents

1. [Features](#features)
2. [Technologies Used](#technologies-used)
3. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Running the Application](#running-the-application)
4. [Testing](#testing)
5. [CI/CD Workflows](#ci/cd-workflows)
6. [Future Enhancements](#future-enhancements)
7. [Contributing](#contributing)
8. [License](#license)

---

## Features

- **FAISS Integration:** Efficient indexing and search capabilities.
- **OpenAI GPT Models:** Generate summaries with clickable citations.
- **FastAPI Framework:** High-performance web framework for building APIs.
- **CI/CD:** Automated workflows for linting, testing, and deployment.
- **Dockerized Deployment:** Simplified application setup and deployment.

---

## Technologies Used

- **Python 3.12**
- **FastAPI**
- **Uvicorn**
- **OpenAI API**
- **FAISS**
- **Docker**
- **Poetry**
- **GitHub Actions**

---

## Getting Started

### Prerequisites

Ensure you have the following installed:

- **Python 3.12+**
- **Poetry** for dependency management
- **Docker** and **Docker Compose** for containerized deployments
- An OpenAI API Key stored in an `.env` file:

  ```env
  OPENAI_API_KEY=your_openai_api_key_here
  ```

### Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd Ethikon-Institute-citizenAI
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

3. Set up the environment:

   - Create a `.env` file and add your OpenAI API key.

   ```bash
   OPENAI_API_KEY=
   ```

4. Build Docker images:
   ```bash
   docker-compose build
   ```

---

## Running the Application

### Using Poetry

Run the application locally with:

```bash
poetry run uvicorn app_fastapi:app --reload
```

Access the application at `http://127.0.0.1:8000`.

### Using Docker

Run the application in a container:

```bash
docker-compose up
```

Access the application at `http://127.0.0.1:8000`.

---

## Testing

The test suite includes two categories of tests: **local** and **CI**.

### **Local Tests**

- Local tests ensure that the OpenAI API key is properly set in the environment and valid.
- These tests require access to the OpenAI API and validate API responses to confirm the key's validity.

### **CI Tests**

- CI tests focus on broader application functionality, such as endpoint behavior, code quality, and FAISS index loading.
- These tests do not require external API calls, ensuring reliability in CI environments.

### Using Poetry

Run all the test (local and CI) suite with:

```bash
poetry run pytest --cov=.
```

Run only local tests:

```bash
poetry run pytest tests/local --cov=.
```

Run only CI tests:

```bash
poetry run pytest tests/ci --cov=.
```

Check code quality:

```bash
poetry run black --check .
poetry run isort --check-only .
```

### Using Docker

Run the test suite with:

```bash
docker-compose run app bash

```

```bash
poetry run pytest --cov=.
```

---

## CI/CD Workflows

This project includes the following GitHub Actions workflows:

1. **Checks Workflow (`.github/workflows/checks.yml`)**

   - Runs linters (Black, isort) and test suites.

2. **Deploy Workflow (`.github/workflows/deploy.yml`)**
   - (Placeholder for deployment logic to platforms like Appliku.)

---

## Future Enhancements

- Integrate deployment logic into `deploy.yml`.
- Enhance error handling and logging mechanisms.
- Add more tests for edge cases.
- Implement new ai features

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`.
3. Commit your changes: `git commit -m "Add some feature"`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Open a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For questions or suggestions, reach out to **Support**
