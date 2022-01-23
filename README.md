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
  
