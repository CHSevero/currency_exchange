# Product Requirements Document (PRD)

**Project:** Currency Converter REST API
**Date:** May 14, 2025
**Author:** Carlos Severo
**Version:** 1.0

---

## 1. Executive Summary

Build a RESTful API service that enables users to convert currency amounts between at least four currencies (BRL, USD, EUR, JPY) using live exchange rates from an external service. The API must track and persist all conversion transactions per user, support querying user transaction history, and provide robust error handling.

---

## 2. Product Purpose and Goals

**Purpose:**
To provide a reliable, accurate, and easy-to-use currency conversion API that supports user-specific transaction tracking and leverages up-to-date exchange rates.

**Goals:**

- Support currency conversion among BRL, USD, EUR, and JPY.
- Use live exchange rates from `http://api.exchangeratesapi.io/latest?base=EUR`.
- Persist all conversion transactions with full details in an embedded database.
- Provide endpoints for conversion and transaction history retrieval by user.
- Ensure clear error responses and robust input validation.
- Deliver a well-tested, documented, and maintainable codebase.

---

## 3. Target Audience \& User Personas

- **Developers** integrating currency conversion into apps or services.
- **Financial analysts** needing conversion transaction logs.
- **End users** who want to track their currency conversions and history.

---

## 4. Key Features \& Requirements

| Feature | Description | Priority |
| :-- | :-- | :-- |
| Currency Conversion | Convert amounts between BRL, USD, EUR, JPY using latest exchange rates. | Must-have |
| Transaction Persistence | Store transaction details: user ID, source/dest currencies, amounts, rate, timestamp. | Must-have |
| User Transaction History | Endpoint to list all conversions by user ID. | Must-have |
| External API Integration | Fetch and cache exchange rates from exchangeratesapi.io with EUR as base currency. | Must-have |
| Error Handling | Return appropriate HTTP status codes and descriptive error messages for failures. | Must-have |
| Embedded Database | Use embedded DB (e.g., SQLite) for storing transactions. | Must-have |
| Testing | Unit and integration tests covering core functionality. | Must-have |
| Documentation | API docs (Swagger/OpenAPI), README with setup and usage instructions. | Must-have |
| Logging and Exception Handling | Centralized logging and global error handlers. | Should-have |


---

## 5. User Stories \& Use Cases

- **As a user**, I want to convert an amount from USD to BRL so that I can know the equivalent value.
- **As a user**, I want my conversion transactions saved so I can review my past conversions.
- **As a developer**, I want clear error messages when I provide invalid input so I can debug easily.
- **As a product owner**, I want the system to fetch live exchange rates but minimize external API calls to avoid rate limits.

---

## 6. Technical Requirements

- **API Framework:** FastAPI with Python 3.13
- **Database:** Embedded SQLite for transaction persistence
- **External API:** `http://api.exchangeratesapi.io/latest?base=EUR` for exchange rates
- **Caching:** In-memory or Redis cache for exchange rates with TTL
- **Testing:** pytest for unit and integration tests
- **Documentation:** Auto-generated Swagger UI via FastAPI
- **Logging:** Python standard logging with structured logs
- **Error Handling:** Global exception handlers returning JSON error responses

---

## 7. UX/UI Requirements

- API must provide clear, consistent JSON responses.
- Use standard HTTP status codes (200, 400, 404, 500, etc.).
- Include detailed error messages in response bodies.
- Provide API documentation accessible via `/docs`.

---

## 8. Assumptions and Constraints

- External API limits requests; caching is necessary to avoid throttling.
- Only four currencies supported initially; extensibility planned for future.
- Embedded DB limits scalability but suffices for MVP and demo.
- User authentication is out of scope; user ID is passed as a parameter.

---

## 9. Risks and Mitigations

| Risk | Mitigation |
| :-- | :-- |
| External API downtime | Cache last known rates and return stale data if needed |
| Rate limit exceeded | Implement caching and retry mechanisms |
| Data consistency in DB | Use transactions and proper session management |
| Incorrect currency input | Validate inputs strictly and return errors |


---

## 10. Open Questions

- Should user authentication be added in future iterations?
- What is the expected transaction volume to plan scaling?
- Are there plans to support more currencies or historical rates?

---

## 11. Change Log

| Version | Date | Description | Author |
| :-- | :-- | :-- | :-- |
| 1.0 | 2025-05-14 | Initial PRD creation | Carlos Severo |
