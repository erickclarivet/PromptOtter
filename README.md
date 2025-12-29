# PromptOtter AI Image Generator

An AI-driven image generation system that automates content creation for Instagram by processing user prompts from post comments. The system validates, filters, and generates images based on community-submitted prompts, then posts the results as Instagram carousels.

## Features

- **Prompt Processing**: Automatically extracts and validates user prompts from Instagram comments
- **AI-Powered Filtering**: Uses OpenAI GPT and HuggingFace models to filter eligible prompts and detect NSFW content
- **Multilingual Support**: Translates prompts using DeepL API for broader accessibility
- **Image Generation**: Creates images from prompts using HuggingFace's AI models
- **User Attribution**: Generates personalized user cards featuring the prompt creator
- **Automated Posting**: Publishes generated content as Instagram carousel posts
- **Content Safety**: Implements multiple layers of content filtering and moderation

## Tech Stack

- **Language**: Python 3.8+
- **AI/ML**: OpenAI GPT-4, HuggingFace Transformers
- **APIs**:
  - Instagram Graph API
  - DeepL Translation API
  - HuggingFace Inference API
  - ImgBB Image Hosting
  - HTML-to-Image conversion
- **Libraries**: Requests, Pydantic, Pillow, python-dotenv
- **Deployment**: Designed for server environments with scheduled execution

## Project Architecture

The system follows a modular architecture with clear separation of concerns:

```
src/
├── botService.py          # Main orchestration service
├── crowdArt.py            # Core business logic (assumed)
├── logger.py              # Logging utilities
├── api/                   # External API integrations
│   ├── deepLApi.py        # Translation services
│   ├── htmlToImgApi.py    # HTML to image conversion
│   ├── huggingFaceApi.py  # AI image generation
│   ├── imgbbApi.py        # Image hosting
│   └── instaApi.py        # Instagram API client
└── html/                  # UI templates
    ├── card.html          # User attribution card template
    └── style.css          # Styling for cards
```

**High-Level Flow**:
1. Fetch recent Instagram post comments
2. Validate and filter prompts using AI classification
3. Translate prompts for consistency
4. Generate images using AI models
5. Create user attribution cards
6. Upload images to hosting service
7. Post carousel to Instagram

## Installation

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv recommended)

### Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd PromptOtter
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# OpenAI API Key for prompt classification
OPENAI_API_KEY=your_openai_api_key_here

# DeepL API Key for translation
DEEPL_API_KEY=your_deepl_api_key_here

# HuggingFace API Key for image generation
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# ImgBB API Key for image hosting
IMGBB_API_KEY=your_imgbb_api_key_here

# Instagram Graph API credentials
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id_here

# html to Image API endpoint (if self-hosted)
HCTI_API_KEY=your_html_to_image_api_key_here
HCTI_API_USER_ID=your_html_to_image_api_user_id_here

# Optional: Logging level
LOG_LEVEL=INFO
```

### API Setup

1. **OpenAI**: Obtain API key from [OpenAI Platform](https://platform.openai.com/)
2. **DeepL**: Get API key from [DeepL API](https://www.deepl.com/pro-api)
3. **HuggingFace**: Create token at [HuggingFace Settings](https://huggingface.co/settings/tokens)
4. **ImgBB**: Get API key from [ImgBB API](https://api.imgbb.com/)
5. **HTML to Image**: Sign up at [HTML/CSS to Image](https://htmlcsstoimage.com/) for API access
6. **Instagram**: Set up Instagram Graph API access through Meta Developer Console

## Usage

### Running the Bot

1. Ensure all environment variables are configured
2. Activate the virtual environment
3. Run the main service:

```bash
python -m src.crowdArt
```

### Manual Testing

You can test individual components:

```python
from src.botService import BotService

bot = BotService()
# Select a prompt from recent comments
prompt, username = bot.select_prompt(media_id="your_media_id")
# Generate image
image_url = bot.generate_image_from_prompt(prompt, "output.png")
# Create user card
card_url = bot.generate_user_card(prompt, username, "profile_image_url")
# Publish carousel
bot.publish_medias([image_url, card_url], f"Generated from @{username}'s prompt: {prompt}")
```

## Instagram Integration

The system integrates with Instagram through the Graph API to:

- Fetch comments from posts
- Create media containers for carousels
- Publish automated content

**Example Account**: The system is designed to work with accounts like [@promptotter](https://www.instagram.com/promptotter), where users submit prompts in comments for AI-generated art.

**API Permissions Required**:
- `instagram_basic`
- `instagram_content_publish`
- `pages_read_engagement`

## Development Notes

### Code Structure
- Use `src/` as the main package directory
- Follow PEP 8 style guidelines
- Add type hints for better code maintainability
- Use the logger module for consistent logging

### Testing
- Create unit tests for API clients in `tests/` directory
- Mock external API calls for reliable testing
- Test prompt validation logic thoroughly

### Adding New Features
- Extend API clients in `src/api/` for new integrations
- Update the `BotService` class for new workflows
- Modify HTML templates in `src/html/` for UI changes

## Security Notes

### API Keys and Secrets
- **Never commit** `.env` files or API keys to version control
- Use environment-specific configuration files
- Rotate API keys regularly
- Consider using secret management services (AWS Secrets Manager, Azure Key Vault) in production

### Content Safety
- Multiple layers of NSFW detection prevent inappropriate content
- User prompts are validated and filtered before processing
- Generated images should be reviewed in production environments

### Best Practices
- Implement rate limiting for API calls
- Use HTTPS for all external communications
- Log sensitive operations without exposing credentials
- Regular security audits of dependencies

## Roadmap

### Planned Improvements
- **Enhanced AI Models**: Integrate additional image generation models (DALL-E, Midjourney API)
- **Advanced Filtering**: Implement more sophisticated content moderation
- **Multi-Platform Support**: Extend to other social media platforms
- **User Dashboard**: Web interface for managing prompts and viewing analytics
- **Batch Processing**: Handle multiple prompts simultaneously
- **Quality Metrics**: Automated evaluation of generated image quality
- **Internationalization**: Support for additional languages beyond DeepL coverage

### Community Contributions
- Open to pull requests for bug fixes and feature enhancements
- Follow contribution guidelines for code quality standards

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This README assumes standard Python development practices. Some implementation details may vary based on specific deployment environments or API changes.