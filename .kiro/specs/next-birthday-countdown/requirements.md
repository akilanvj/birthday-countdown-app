# Requirements Document

## Introduction

NextBirthdayCountdown is an Azure serverless demo project that calculates when someone's next birthday will occur. The system consists of a Python Azure Functions backend API and a simple HTML/CSS/JavaScript frontend dashboard. This project serves as a homework/demo showcasing Azure Functions v2 programming model with a clean, minimal implementation.

## Glossary

- **Backend_API**: The Azure Functions Python application that processes birthday calculations
- **Frontend_Dashboard**: The static HTML/CSS/JavaScript application that provides the user interface
- **DOB**: Date of birth in ISO YYYY-MM-DD format
- **Next_Birthday**: The next occurrence of a person's birthday from the current date
- **Leap_Year_Handler**: Component that manages February 29 birthday edge cases

## Requirements

### Requirement 1: HTTP API Endpoint

**User Story:** As a developer, I want a REST API endpoint for birthday calculations, so that I can integrate birthday countdown functionality into applications.

#### Acceptance Criteria

1. THE Backend_API SHALL expose an HTTP GET endpoint at exactly `/api/nextbirthday`
2. WHEN a request is made to the endpoint, THE Backend_API SHALL accept a query parameter named `dob`
3. THE Backend_API SHALL require the `dob` parameter to be in ISO YYYY-MM-DD format
4. WHEN a valid request is processed, THE Backend_API SHALL return HTTP status 200 with JSON response
5. THE Backend_API SHALL use Python Azure Functions v2 programming model

### Requirement 2: Input Validation

**User Story:** As a system, I want to validate date inputs, so that I can prevent invalid calculations and provide clear error messages.

#### Acceptance Criteria

1. WHEN the `dob` parameter is missing, THE Backend_API SHALL return HTTP 400 with error message
2. WHEN the `dob` parameter format is invalid, THE Backend_API SHALL return HTTP 400 with error message
3. WHEN the `dob` represents a future date, THE Backend_API SHALL return HTTP 400 with error message
4. WHEN returning errors, THE Backend_API SHALL include an example usage in the response
5. THE Backend_API SHALL validate dates using the local server date without timezone considerations

### Requirement 3: Birthday Calculation Logic

**User Story:** As a user, I want accurate birthday calculations, so that I can know exactly when my next birthday occurs.

#### Acceptance Criteria

1. WHEN calculating age, THE Backend_API SHALL determine the current age in complete years
2. WHEN determining next birthday, THE Backend_API SHALL find the next occurrence of the birth date
3. WHEN calculating days until birthday, THE Backend_API SHALL count calendar days from today to next birthday
4. THE Backend_API SHALL determine the day of the week for the next birthday date
5. THE Backend_API SHALL generate a friendly message indicating days until next birthday

### Requirement 4: Leap Year Handling

**User Story:** As a person born on February 29, I want my birthday handled correctly in non-leap years, so that I still have a birthday celebration date.

#### Acceptance Criteria

1. WHEN a person's DOB is February 29, THE Leap_Year_Handler SHALL check if the next birthday year is a leap year
2. IF the next birthday year is not a leap year, THE Leap_Year_Handler SHALL use February 28 as the next birthday date
3. IF the next birthday year is a leap year, THE Leap_Year_Handler SHALL use February 29 as the next birthday date
4. THE Leap_Year_Handler SHALL apply this logic consistently for all February 29 birthdays

### Requirement 5: JSON Response Format

**User Story:** As a frontend developer, I want a consistent JSON response format, so that I can reliably parse and display birthday information.

#### Acceptance Criteria

1. THE Backend_API SHALL return successful responses with exactly these fields: `inputDob`, `ageYears`, `nextBirthdayDate`, `nextBirthdayDayOfWeek`, `daysUntilNextBirthday`, `message`
2. THE Backend_API SHALL format the `inputDob` field as the original input date string
3. THE Backend_API SHALL format the `nextBirthdayDate` field in ISO YYYY-MM-DD format
4. THE Backend_API SHALL format the `nextBirthdayDayOfWeek` field as the full day name (e.g., "Friday")
5. THE Backend_API SHALL format the `message` field with emoji and friendly text

### Requirement 6: Error Response Format

**User Story:** As a frontend developer, I want consistent error responses, so that I can handle and display errors appropriately.

#### Acceptance Criteria

1. THE Backend_API SHALL return error responses with exactly these fields: `error`, `example`
2. THE Backend_API SHALL provide human-readable error messages in the `error` field
3. THE Backend_API SHALL include a usage example in the `example` field showing correct format
4. THE Backend_API SHALL return HTTP 400 status for all validation errors
5. THE Backend_API SHALL format error responses as valid JSON

### Requirement 7: Frontend Dashboard Interface

**User Story:** As a user, I want a simple web interface to check birthday countdowns, so that I can easily use the birthday calculation service.

#### Acceptance Criteria

1. THE Frontend_Dashboard SHALL provide a clean UI card with date input field for DOB
2. THE Frontend_Dashboard SHALL include a "Calculate" button to trigger birthday calculation
3. THE Frontend_Dashboard SHALL display output fields for age, days until birthday, next birthday date, and day of week
4. THE Frontend_Dashboard SHALL show the friendly message returned from the API
5. THE Frontend_Dashboard SHALL implement client-side validation for empty or invalid DOB inputs

### Requirement 8: API Integration

**User Story:** As a frontend application, I want to communicate with the backend API, so that I can retrieve and display birthday calculations.

#### Acceptance Criteria

1. THE Frontend_Dashboard SHALL use the fetch() API to make HTTP requests to the backend
2. THE Frontend_Dashboard SHALL have a configurable API base URL with default `http://localhost:7071/api/nextbirthday`
3. WHEN API calls succeed, THE Frontend_Dashboard SHALL display the returned data in the UI
4. WHEN API calls fail, THE Frontend_Dashboard SHALL display error messages nicely in the UI
5. THE Frontend_Dashboard SHALL handle both network errors and API error responses

### Requirement 9: Project Structure and Files

**User Story:** As a developer, I want a well-organized project structure, so that I can easily understand, deploy, and maintain the application.

#### Acceptance Criteria

1. THE Backend_API SHALL be implemented in `function_app.py` containing the function and routing
2. THE Backend_API SHALL include `requirements.txt`, `host.json`, and `local.settings.json` files
3. THE Frontend_Dashboard SHALL be organized in a `/frontend` folder with `index.html`, `styles.css`, and `app.js`
4. THE project SHALL include a comprehensive `README.md` with setup, deployment, and usage instructions
5. THE Backend_API SHALL prefer standard library dependencies only

### Requirement 10: Deployment and CORS Configuration

**User Story:** As a developer, I want clear deployment instructions and CORS configuration, so that I can deploy the application to Azure and enable frontend access.

#### Acceptance Criteria

1. THE README SHALL include Azure deployment steps using Azure CLI
2. THE README SHALL provide CORS configuration guidance for allowing frontend origins
3. THE README SHALL document two deployment options: Azure Static Web Apps and simple static hosting
4. THE project SHALL be ready to copy into a repository on Mac and run locally
5. THE code SHALL be clean, commented, and minimal for demo purposes