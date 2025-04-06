# HarvardX CS50 Web Programming with Python and JavaScript

My solutions and implementations of CS50's Web Programming with Python and JS course's projects
 

### Search:
- three-pages UI to access basic Google Search, Google Image Search and Google Advanced Search functionality
 
### Wiki:
- Python's Django based web application to emulate Wiki creation engine
- Some JavaScript to manage forms' input
- Available functionality:
  - list all pages, view single page content, view random page content, create new page, edit page
  - support of the following Markdown tags (implemented using RegEx): headings, bold text, italic text, links, ordered and unordered lists, paragraphs

### Commerce:
- Python's Django based web application of demo auctions (eBay inspired) website
- Python/Django/SQLite backend (using class-based views), Celery (with Redis) workers for some tasks created by Django signals handlers, Bootstrap/jQuery powered front-end
- unittesting of some functionalities (not complete) including some front-end testing with Selenium (Firefox webdriver)
- Available functionality:
  - user account management: signup with confirmation by email (by default uses built-in Django filebased backend with modifications  - content of confirmation email is displayed on web page instead of actual emal sending), password change/reset, profile creation/update, activities summary
  - listing management: create/modify product, list product/mofidy listing/cancel listing, bid on active listings, comment on active listing/answer comments, watch/unwatch listings, mark listing as paid/sent/delivered
  - messenger: communication between product's seller and buyer, system messages
  - general: product categories, full text search in products/listings title and description (implemented using RegEx; could be extended with additional functionality in case of PostgreSQL usage), admin website

### Mail:
- Python's Django based back-end wed-application with a simple web API
- Plain JavaScript (ES6) realization of SPA to implement simple email client
- Available functionality:
  - separate Inbox, Sent and Archived mailboxes
  - compose new email
  - view email message
  - reply email message
  - message can be sent to a list of recipients
  - archive / unarchive email messaage
  

# WiseGrocery

WiseGrocery is a comprehensive grocery management application designed to help users manage their food inventory, plan meals, track food expiration, and generate shopping lists.

## Project Structure

```
wisegrocery/
├── wg-frontend/      # React Native/Expo mobile application
├── wg-backend/       # Django REST API backend
├── .venv/            # Python virtual environment
├── requirements.txt  # Python dependencies
└── umlchart.uxf      # UML diagram file
```

## Features

- **Inventory Management**: Track food items in multiple storage locations (fridge, freezer, pantry)
- **Equipment Management**: Define different storage equipment with temperature ranges
- **Recipe Management**: Create and store recipes with required ingredients
- **Meal Planning**: Plan meals for different days and meal types
- **Shopping List Generation**: Generate shopping lists based on meal plans and inventory
- **Expiration Tracking**: Monitor food expiration dates and receive notifications
- **Consumption Tracking**: Track food usage and consumption patterns

## Technology Stack

### Backend (wg-backend)
- **Framework**: Django with Django REST Framework
- **Database**: SQLite (development) / Can be configured for production
- **Task Queue**: Celery for background tasks (expiration notifications, etc.)
- **API**: RESTful API endpoints for all functionality

### Frontend (wg-frontend)
- **Framework**: React Native with Expo
- **State Management**: Redux with Redux Toolkit
- **Navigation**: React Navigation
- **UI Components**: React Native Paper
- **API Integration**: Axios

## Setup and Installation

See wisegrocery/README.md file for details.

## Core Models

- **User**: Extended Django user model for authentication
- **Equipment**: Storage locations (refrigerator, pantry, etc.)
- **Product**: Food items with details like categories, temperature requirements
- **Recipe**: Collection of products with quantities for meal preparation
- **CookingPlan**: Schedule for meal preparation
- **Purchase**: Record of grocery shopping
- **StockItem**: Individual inventory items with expiration dates
- **Consumption**: Record of product usage

## Key Components

### Shopping Module

The `Shopping` class provides the core functionality for generating intelligent shopping lists based on user configurations and needs:

- **Smart Shopping List Generation**: Creates shopping lists based on:
  - Current cooking plans and recipes
  - Historical consumption data
  - Minimum stock requirements
  - Current inventory levels
  
- **Configurable Shopping Logic**: Users can customize their shopping experience:
  - Base shopping lists on cooking plans
  - Use historical consumption data for recurring items
  - Set minimum stock thresholds for essential items
  
- **Stock Management Integration**: Automatically accounts for:
  - Current stock levels
  - Available storage space in appropriate equipment
  - Temperature requirements of products
  
- **Unit Conversion Support**: Handles different units of measurement with automatic conversion

The shopping list generation algorithm follows these steps:
1. Calculate needed product quantities from active cooking plans
2. Analyze historical consumption patterns
3. Compare with minimum stock levels for each product
4. Adjust based on current inventory
5. Generate the final shopping list with precise quantities

## Development

The application follows a client-server architecture with a RESTful API:

1. The Django backend provides API endpoints for all data operations
2. The React Native frontend consumes these APIs for user interaction
3. Background tasks handle scheduled operations like expiration checking

## License

This project is for educational purposes as part of the CS50 Web Development with Python and JavaScript course.
  
