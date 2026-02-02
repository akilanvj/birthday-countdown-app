# Implementation Plan: NextBirthdayCountdown

## Overview

This implementation plan breaks down the NextBirthdayCountdown project into discrete coding tasks. The approach follows an incremental development pattern, building the Azure Functions backend first, then the frontend dashboard, and finally integrating them together. Each task builds on previous work and includes validation through testing.

## Tasks

- [x] 1. Set up Azure Functions project structure
  - Create `function_app.py` with basic Azure Functions v2 app initialization
  - Create `requirements.txt` with minimal dependencies (azure-functions only)
  - Create `host.json` with basic configuration
  - Create `local.settings.json` template with CORS settings for local development
  - _Requirements: 1.5, 9.1, 9.2_

- [x] 2. Implement input validation and error handling
  - [x] 2.1 Create input validator for DOB parameter
    - Implement validation for missing parameter
    - Implement validation for invalid date format (non-ISO YYYY-MM-DD)
    - Implement validation for future dates
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ]* 2.2 Write property test for input validation
    - **Property 2: Invalid input produces error response**
    - **Validates: Requirements 2.2, 2.3, 6.1, 6.4**
  
  - [x] 2.3 Create error response formatter
    - Implement consistent error JSON structure with `error` and `example` fields
    - Ensure HTTP 400 status for validation errors
    - _Requirements: 6.1, 6.3, 6.4, 6.5_

- [x] 3. Implement core birthday calculation logic
  - [x] 3.1 Create birthday calculator module
    - Implement age calculation in complete years
    - Implement next birthday date calculation
    - Implement days until birthday counting
    - Implement day of week determination
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ]* 3.2 Write property test for age calculation
    - **Property 3: Age calculation accuracy**
    - **Validates: Requirements 3.1**
  
  - [ ]* 3.3 Write property test for next birthday calculation
    - **Property 4: Next birthday calculation**
    - **Validates: Requirements 3.2**
  
  - [ ]* 3.4 Write property test for days until birthday
    - **Property 5: Days until birthday accuracy**
    - **Validates: Requirements 3.3**

- [x] 4. Implement leap year handling for February 29 birthdays
  - [x] 4.1 Create leap year handler
    - Implement leap year detection logic
    - Implement February 29 to February 28 conversion for non-leap years
    - Integrate with birthday calculator
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ]* 4.2 Write property test for leap year handling
    - **Property 6: February 29 leap year handling**
    - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 5. Create HTTP endpoint and response formatting
  - [x] 5.1 Implement HTTP trigger function
    - Create `/api/nextbirthday` GET endpoint using Azure Functions v2 decorators
    - Integrate input validation, birthday calculation, and error handling
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 5.2 Implement success response formatter
    - Create JSON response with all required fields: inputDob, ageYears, nextBirthdayDate, nextBirthdayDayOfWeek, daysUntilNextBirthday, message
    - Implement friendly message generation with emoji
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 3.5_
  
  - [ ]* 5.3 Write property test for response format
    - **Property 1: Valid input produces complete response**
    - **Validates: Requirements 1.4, 5.1**
  
  - [ ]* 5.4 Write property test for response format consistency
    - **Property 7: Response format consistency**
    - **Validates: Requirements 5.2, 5.3, 5.4**
  
  - [ ]* 5.5 Write property test for message content
    - **Property 8: Message content validation**
    - **Validates: Requirements 3.5, 5.5**

- [x] 6. Checkpoint - Backend API complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Create frontend project structure
  - Create `/frontend` directory
  - Create `index.html` with basic HTML structure and form elements
  - Create `styles.css` with clean, responsive card-based layout
  - Create `app.js` with configurable API base URL (default: http://localhost:7071/api/nextbirthday)
  - _Requirements: 9.3, 8.2_

- [x] 8. Implement frontend user interface
  - [x] 8.1 Build HTML form and display elements
    - Create date input field for DOB
    - Create "Calculate" button
    - Create output display areas for age, days until birthday, next birthday date, day of week
    - Create area for friendly message display
    - Create error message display area
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 8.2 Implement CSS styling
    - Style the UI card with clean, modern appearance
    - Add responsive design for different screen sizes
    - Style error states and success states
    - _Requirements: 7.1_

- [x] 9. Implement frontend JavaScript functionality
  - [x] 9.1 Create form handling and client-side validation
    - Implement validation for empty DOB input
    - Implement basic date format validation
    - Prevent API calls for invalid inputs
    - _Requirements: 7.5_
  
  - [ ]* 9.2 Write unit test for frontend input validation
    - **Property 10: Frontend input validation**
    - **Validates: Requirements 7.5**
  
  - [x] 9.3 Implement API communication using fetch()
    - Create function to call backend API with DOB parameter
    - Handle successful API responses and display results in UI
    - Handle API error responses and network failures
    - Display errors nicely in the UI
    - _Requirements: 8.1, 8.3, 8.4, 8.5_
  
  - [ ]* 9.4 Write unit test for frontend error handling
    - **Property 9: Frontend error handling**
    - **Validates: Requirements 8.4, 8.5**

- [x] 10. Create project documentation
  - [x] 10.1 Write comprehensive README.md
    - Add project overview and features
    - Add local development setup instructions
    - Add Azure deployment steps using Azure CLI
    - Add CORS configuration guidance
    - Add usage examples and API documentation
    - Document two deployment options: Azure Static Web Apps and simple static hosting
    - _Requirements: 9.4, 10.1, 10.2, 10.3_

- [x] 11. Final integration and testing
  - [x] 11.1 Test local development setup
    - Verify Azure Functions local development works
    - Verify frontend can connect to local backend
    - Test CORS configuration for local development
    - _Requirements: 10.4_
  
  - [ ]* 11.2 Write integration tests
    - Test end-to-end API calls from frontend to backend
    - Test error scenarios with real HTTP requests
    - Verify CORS functionality

- [x] 12. Final checkpoint - Complete system
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation uses Python Azure Functions v2 programming model
- Standard library dependencies are preferred for the backend
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests ensure frontend-backend communication works correctly