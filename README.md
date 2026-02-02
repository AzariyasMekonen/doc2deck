# Doc2Deck - PDF to PowerPoint Converter

A professional web application that converts PDF documents into structured notes and PowerPoint presentations using AI technology with presentation management capabilities.

## Features

- **Secure Authentication**: JWT-based user registration and login system
- **PDF Processing**: Upload and extract text from specific PDF pages
- **AI-Powered Notes**: Generate structured study notes using OpenRouter Trinity or enhanced fallback processing
- **PowerPoint Generation**: Convert notes into professionally styled presentations
- **AI Review**: Get comprehensive feedback on presentation quality and structure
- **Presentation Management**: Save, organize, and access multiple presentations
- **PPT Viewer**: Navigate through slides with keyboard controls
- **PPT Presenter**: Full-screen presentation mode with professional styling
- **User Management**: Individual user data organization and session management

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy
- **Authentication**: JWT tokens with SHA256 password hashing
- **PDF Processing**: PyPDF2, pdfplumber
- **Presentation Generation**: python-pptx with custom styling
- **AI Integration**: OpenRouter Trinity model with enhanced fallback
- **Frontend**: HTML with Tailwind CSS and JavaScript

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenRouter API key (optional - fallback processing available)

### Setup

1. **Clone and navigate to the project**
   ```bash
   git clone <repository-url>
   cd Doc2Deck
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - Copy `.env.example` to `.env`
   - Add your OpenRouter API key to the `.env` file (optional)
   - Get API key from: https://openrouter.ai/

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Open browser to `http://localhost:8000`
   - Register an account and start using the application

## Usage

1. **Register/Login**: Create an account or sign in
2. **Upload PDF**: Select a PDF file, add title, and specify pages to process
3. **Generate Notes**: AI creates structured study notes from the PDF content
4. **Edit Notes**: Review and modify the generated notes with live preview
5. **Manage Presentations**: Access all your saved presentations from the dashboard
6. **Create Presentation**: Convert notes into a styled PowerPoint presentation
7. **View/Present**: Use the built-in viewer or full-screen presenter mode
8. **Download**: Get your presentation file for offline use

## Key Features

### Presentation Management
- Save multiple presentations per user
- Organize presentations with titles and creation dates
- Quick access to edit, view, present, and download
- Individual presentation tracking

### AI Processing
- Primary: OpenRouter Trinity model for high-quality notes
- Fallback: Enhanced local processing for reliable operation
- Comprehensive feedback (up to 10 points) on presentation quality
- Paragraph-based notes generation (not bullet points)

### Presentation Tools
- **Viewer**: Navigate slides with controls and keyboard shortcuts
- **Presenter**: Full-screen mode with professional styling
- **Keyboard Navigation**: Arrow keys, spacebar, F11, ESC support
- **Responsive Design**: Works on different screen sizes

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User authentication
- `GET /logout` - User logout

### Core Features
- `GET /dashboard` - Main dashboard with presentation overview
- `GET /presentations` - Presentation management page
- `POST /upload` - PDF upload and processing with title
- `GET /notes/{id}` - Notes viewer and editor for specific presentation
- `POST /notes/{id}/save` - Save notes for specific presentation
- `POST /generate-ppt` - PowerPoint generation
- `GET /view-ppt/{id}` - Presentation viewer
- `GET /present-ppt/{id}` - Presentation presenter mode
- `GET /download-ppt/{id}` - Download presentation file

## Project Structure

```
Doc2Deck/
├── app/
│   ├── auth/
│   │   ├── models.py      # User and Presentation models
│   │   └── auth.py        # Authentication service
│   ├── pdf/
│   │   └── processor.py   # PDF text extraction
│   ├── ai/
│   │   └── service.py     # AI integration with fallback
│   └── ppt/
│       └── generator.py   # PowerPoint generation with styling
├── templates/
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # Main dashboard
│   ├── presentations.html # Presentation management
│   ├── upload.html       # PDF upload page
│   ├── notes.html        # Notes editor with preview
│   ├── ppt_review.html   # PPT review and generation
│   ├── view_ppt.html     # Presentation viewer
│   └── present_ppt.html  # Presentation presenter
├── uploads/              # File storage
├── main.py              # FastAPI application
├── requirements.txt     # Dependencies
├── .env.example        # Environment template
└── README.md           # This file
```

## Configuration

Environment variables in `.env`:
- `SECRET_KEY`: JWT signing key
- `OPENROUTER_API_KEY`: OpenRouter API key (optional)
- `DATABASE_URL`: Database connection string
- `UPLOAD_DIR`: File upload directory

## Dependencies

- **fastapi** - Web framework
- **uvicorn[standard]** - ASGI server
- **python-multipart** - File upload support
- **python-jose[cryptography]** - JWT tokens
- **passlib[bcrypt]** - Password hashing
- **sqlalchemy** - Database ORM
- **pydantic** - Data validation
- **PyPDF2** - PDF processing
- **pdfplumber** - Enhanced PDF text extraction
- **python-pptx** - PowerPoint generation
- **google-generativeai** - AI integration (fallback)
- **requests** - HTTP requests
- **jinja2** - Template engine
- **aiofiles** - Async file operations

## License

This project is for educational and professional use. Made by Azariyas Mekonen 2025