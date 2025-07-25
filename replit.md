# KrishiMitra - Agricultural Platform

## Overview

KrishiMitra is a comprehensive agricultural platform built with Flask that connects farmers, customers, shopkeepers, and shelter owners in a unified ecosystem. The platform features Netflix-style animations, glassmorphism design, and attractive visual elements. The platform facilitates crop trading, storage booking, and marketplace transactions while providing role-based access and secure authentication.

## Recent Changes (July 2025)

### Farmer Dashboard Enhancement
- Enhanced background with radial gradient overlays and improved visual depth
- Added weather widget showing current conditions (28°C, Sunny)
- Implemented animated statistics cards with hover effects and progress indicators
- Added floating action button (FAB) with pulsing animation for quick crop upload
- Enhanced sidebar with shimmer effects and improved navigation animations
- Upgraded welcome text with gradient text animation and sliding underline
- Added progress tracking section for Crop Growth (75%), Sales Target (60%), Storage Utilization (85%)
- Improved card animations with Netflix-style video hover effects and 3D transformations
- Enhanced glassmorphism effects with improved backdrop blur and transparency

### Shopkeeper Dashboard Styling
- Redesigned to match farmer dashboard aesthetic with orange/amber theme
- Added marketplace-themed background with 30% transparency overlay
- Implemented same animation system as farmer dashboard
- Features: Browse Crops, My Orders, Saved Sellers, Requests Sent
- Added notification badges and enhanced stat cards

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with SQLite (default) or PostgreSQL support
- **Authentication**: Session-based authentication with password hashing
- **Registration System**: Direct user registration with immediate account creation
- **File Handling**: Werkzeug utilities for secure file uploads

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **CSS Framework**: Bootstrap 5.3.2 with custom styling
- **JavaScript**: Vanilla JavaScript with Netflix-style animations
- **Responsive Design**: Mobile-first approach with backdrop filters and glassmorphism effects

### Database Design
The application uses SQLAlchemy with a declarative base model approach:

- **User Model**: Base authentication with role-based access (farmer, customer, shopkeeper, shelter)
- **Role-specific Models**: Farmer, Customer, Shopkeeper, ShelterOwner with foreign key relationships
- **Transaction Models**: Crop, StorageRequest, Purchase for business logic
- **Security Models**: Session-based authentication with password hashing

## Key Components

### Authentication System
- Multi-role user registration and login
- Password hashing using Werkzeug security utilities
- Direct registration system without phone verification
- Session management for user state persistence

### User Role Management
- **Farmers**: Can upload crops, book storage, view orders, access marketplace
- **Customers**: Can browse and purchase crops from farmers
- **Shopkeepers**: Can manage inventory and process orders
- **Shelter Owners**: Can provide storage services to farmers

### File Upload System
- Secure file upload with allowed extensions validation
- Image handling for crop listings
- Static file serving for uploaded content

### Registration System
- Direct user registration without OTP verification
- Immediate account creation and login capability
- Role-based account setup with profile creation

## Data Flow

1. **User Registration**: Direct process with role selection, form validation, and immediate account creation
2. **Authentication**: Login with username/password, session creation, role-based dashboard routing
3. **Crop Management**: Upload, view, and manage crop listings with image support
4. **Marketplace**: Browse available crops, place orders, manage transactions
5. **Storage Booking**: Connect farmers with shelter owners for crop storage
6. **Order Processing**: Track orders from placement to completion

## External Dependencies

### Python Packages
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Login: User session management (referenced but not fully implemented)
- Werkzeug: Password hashing and file utilities

### Frontend Dependencies
- Bootstrap 5.3.2: CSS framework
- Font Awesome 6.4.0: Icon library
- Google Fonts (Poppins, Inter): Typography
- Custom CSS with glassmorphism effects

### Database
- SQLite: Default development database
- PostgreSQL: Production database support via DATABASE_URL environment variable

## Deployment Strategy

### Environment Configuration
- Environment variables for database URL and session secret
- Debug mode configuration for development
- Host and port configuration for deployment flexibility

### Database Management
- Automatic table creation on application startup
- Database connection pooling with SQLAlchemy engine options
- Migration support through SQLAlchemy

### Security Considerations
- Password hashing for user authentication
- Session secret key configuration
- File upload security with extension validation
- Direct user registration without phone verification

### Development Setup
- Flask development server on localhost:5000
- Debug mode enabled for development
- Automatic table creation and sample data handling

The application follows a modular structure with clear separation of concerns between models, routes, and utilities, making it maintainable and scalable for agricultural marketplace operations.