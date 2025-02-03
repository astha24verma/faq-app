# Multilingual FAQ App

A powerful Django REST Framework solution for managing Frequently Asked Questions with automatic translation, Redis caching, and multi-language support.

## 🌟 Features

- **Automatic Translation**: Instant translations using Google Translate
- **Multi-language Support**: Seamless language switching
- **Redis Caching**: High-performance translation storage
- **WYSIWYG Editing**: Rich text support with CKEditor
- **Comprehensive API**: Full CRUD operations
- **Flexible Configuration**: Easy language management

## 🛠 Technology Stack

- **Backend**: Django 4.2+
- **API**: Django REST Framework
- **Translation**: Google Translate
- **Caching**: Redis
- **Text Editing**: django-ckeditor
- **Testing**: pytest
- **Linting**: flake8

## 📋 Prerequisites

- Python 3.10+
- Redis Server
- Virtual Environment
- Google Translate API (optional)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/astha24verma/faq-app.git
cd faq-app
```

### 2. Create Virtual Environment
```bash
# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Settings
```python
# settings.py
INSTALLED_APPS = [
    ...
    'ckeditor',
    'rest_framework',
    'faq_app',
]

# Language Configuration
LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'Hindi'),
    ('bn', 'Bengali'),
    ('es', 'Spanish'),
]

# Redis Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

### 5. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/faqs/` | List all FAQs |
| GET | `/api/faqs/?lang={lang}` | List FAQs in specific language |
| POST | `/api/faqs/` | Create new FAQ |
| GET | `/api/faqs/{id}/` | Get specific FAQ |
| GET | `/api/faqs/{id}/?lang={lang}` | Get FAQ in specific language |
| PUT | `/api/faqs/{id}/` | Update FAQ |
| DELETE | `/api/faqs/{id}/` | Delete FAQ |
| GET | `/api/faqs/available-languages/` | List supported languages |

### Query Parameters
- `lang`: Specify language (e.g., `?lang=hi`)
- `page`: Pagination support
- `page_size`: Items per page

## 🔍 Usage Examples

### Creating a FAQ
```python
# Python
faq = FAQ.objects.create(
    question="How do I reset my password?",
    answer="Click 'Forgot Password' link..."
)
# Automatically translates to configured languages
```

### API Request
```bash
# Get FAQs in Hindi
curl http://localhost:8000/api/faqs/?lang=hi
```

## 🧪 Testing

### Run Tests
```bash
pytest
# With coverage
pytest --cov=.
```

### Code Quality
```bash
flake8
```

## 📦 Project Structure
```
faq_translation_system/
│
├── faq_app/
│   ├── models.py         # Database models
│   ├── views.py          # API views
│   ├── serializers.py    # Data serialization
│   ├── signals.py        # Translation signals
│   └── admin.py          # Admin configuration
│
├── tests/
│   ├── test_models.py
│   └── test_api.py
│
├── requirements.txt
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License

## 🆘 Support

For issues, please open a GitHub issue or contact support@example.com

## 📊 Performance Tips

- Redis caching reduces translation overhead
- Translations are cached for 24 hours
- Implement rate limiting for translation API calls

## 🔮 Future Roadmap

- [ ] Machine Learning Enhanced Translations
- [ ] More Language Support
- [ ] Advanced Caching Strategies
- [ ] Comprehensive Logging
```

## 💡 Pro Tips

- Always keep base content in primary language
- Regularly update translation cache
- Monitor translation API usage and costs
- Implement fallback mechanisms

```bash
# Manually clear translation cache
python manage.py clear_translation_cache
```

## 🚨 Deployment Considerations

- Use environment variables for sensitive configs
- Implement proper authentication
- Monitor API and translation performance
- Set up proper logging and error tracking

Enjoy your multilingual FAQ system! 🌍🚀