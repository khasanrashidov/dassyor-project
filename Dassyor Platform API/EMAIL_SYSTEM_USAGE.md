# Dassyor Dynamic Email System

This document explains how to use the new dynamic email system that allows sending customized emails while maintaining consistent Dassyor styling.

## Features

- ✅ **Dynamic Content**: Create emails with various content blocks (text, buttons, lists, images, etc.)
- ✅ **Consistent Styling**: All emails maintain Dassyor's brand styling automatically
- ✅ **Single Email Sending**: Send individual emails with custom templates
- ✅ **Bulk Email Sending**: Send the same email to multiple recipients with batching
- ✅ **Email Preview**: Preview emails before sending them
- ✅ **Template Examples**: Get pre-built template examples
- ✅ **Health Monitoring**: Check email service health status

## API Endpoints

### 1. Send Single Email

**POST** `/api/admin/email/send`

Requires: `Admin` role

```json
{
  "to_email": "recipient@example.com",
  "template": {
    "subject": "Welcome to Dassyor!",
    "header": {
      "type": "header",
      "title": "Welcome!",
      "subtitle": "Get started with your account"
    },
    "content_blocks": [
      {
        "type": "text",
        "content": "Thank you for joining us!",
        "font_size": 16
      },
      {
        "type": "button",
        "buttons": [
          {
            "text": "Get Started",
            "url": "https://app.dassyor.com/dashboard",
            "color": "#4084f4"
          }
        ],
        "alignment": "center"
      }
    ],
    "include_default_footer": true
  }
}
```

### 2. Send Bulk Emails

**POST** `/api/admin/email/bulk-send`

Requires: `Admin` role

```json
{
  "to_emails": ["user1@example.com", "user2@example.com", "user3@example.com"],
  "template": {
    "subject": "Important Update",
    "content_blocks": [
      {
        "type": "text",
        "content": "We have important updates to share with you.",
        "font_size": 16
      }
    ],
    "include_default_footer": true
  },
  "batch_size": 50
}
```

### 3. Preview Email

**POST** `/api/admin/email/preview`

Requires: `Authentication` (any role)

```json
{
  "template": {
    "subject": "Preview Email",
    "content_blocks": [
      {
        "type": "text",
        "content": "This is a preview of your email.",
        "font_size": 16
      }
    ]
  },
  "to_email": "preview@example.com"
}
```

### 4. Get Template Examples

**GET** `/api/admin/email/templates/examples`

Requires: `Authentication` (any role)

Returns pre-built template examples you can use as starting points.

### 5. Email Service Health Check

**GET** `/api/admin/email/health`

Requires: `Authentication` (any role)

Checks the health of the email service and SMTP connection.

## Content Block Types

### 1. Header Block

```json
{
  "type": "header",
  "title": "Main Title",
  "subtitle": "Optional subtitle",
  "color": "#4084f4"
}
```

### 2. Text Block

```json
{
  "type": "text",
  "content": "Your text content here",
  "font_size": 16,
  "color": "#333",
  "alignment": "left"
}
```

### 3. Button Block

```json
{
  "type": "button",
  "buttons": [
    {
      "text": "Click Me",
      "url": "https://example.com",
      "color": "#4084f4"
    }
  ],
  "alignment": "center"
}
```

### 4. List Block

```json
{
  "type": "list",
  "title": "Optional List Title",
  "list_type": "bullet",
  "items": [
    { "text": "First item" },
    { "text": "Second item" },
    { "text": "Third item" }
  ]
}
```

### 5. Image Block

```json
{
  "type": "image",
  "src": "https://example.com/image.jpg",
  "alt": "Image description",
  "width": 400,
  "height": 200,
  "alignment": "center"
}
```

### 6. Divider Block

```json
{
  "type": "divider",
  "color": "#ddd",
  "height": 1
}
```

### 7. Spacer Block

```json
{
  "type": "spacer",
  "height": 30
}
```

## Template Structure

Every email template has this basic structure:

```json
{
  "subject": "Email Subject",
  "header": {}, // Optional header block
  "content_blocks": [], // Array of content blocks
  "footer_text": "Optional custom footer text",
  "include_default_footer": true // Include Dassyor branding footer
}
```

## Styling Guidelines

The system automatically applies Dassyor's consistent styling:

- **Font**: Google Sans, Verdana, sans-serif
- **Primary Color**: #4084f4
- **Background**: #f4f4f4 (outer), #ffffff (content)
- **Text Color**: #333 (default), #666 (muted)
- **Content Boxes**: #f9f9f9 background with subtle shadows
- **Responsive**: Max-width 600px with proper mobile handling

## Usage Examples

### Welcome Email

```json
{
  "subject": "Welcome to Dassyor!",
  "header": {
    "type": "header",
    "title": "Welcome to Dassyor!",
    "subtitle": "Get started with your new account"
  },
  "content_blocks": [
    {
      "type": "text",
      "content": "Thank you for joining Dassyor! We're excited to have you on board."
    },
    {
      "type": "button",
      "buttons": [
        {
          "text": "Get Started",
          "url": "https://app.dassyor.com/dashboard"
        }
      ],
      "alignment": "center"
    },
    {
      "type": "list",
      "title": "What you can do next:",
      "items": [
        { "text": "Complete your profile setup" },
        { "text": "Create your first project" },
        { "text": "Invite team members" }
      ]
    }
  ]
}
```

### Project Notification Email

```json
{
  "subject": "Project Update Notification",
  "header": {
    "type": "header",
    "title": "Project Update",
    "subtitle": "Important changes to your project"
  },
  "content_blocks": [
    {
      "type": "text",
      "content": "Your project has been updated with new information."
    },
    {
      "type": "divider"
    },
    {
      "type": "text",
      "content": "Changes made:",
      "font_size": 18,
      "color": "#4084f4"
    },
    {
      "type": "list",
      "items": [
        { "text": "Project description updated" },
        { "text": "New collaborator added" },
        { "text": "Status changed to 'In Progress'" }
      ]
    },
    {
      "type": "spacer",
      "height": 30
    },
    {
      "type": "button",
      "buttons": [
        {
          "text": "View Project",
          "url": "https://app.dassyor.com/projects/123"
        }
      ],
      "alignment": "center"
    }
  ]
}
```

## Best Practices

1. **Keep it Simple**: Don't overcomplicate your email templates
2. **Test First**: Always preview emails before sending
3. **Use Consistent Colors**: Stick to the Dassyor color palette
4. **Mobile-Friendly**: The system handles responsive design automatically
5. **Batch Bulk Sends**: Use appropriate batch sizes for bulk emails (default: 50)
6. **Monitor Health**: Check the email service health regularly
7. **Handle Errors**: Always check API responses for error handling

## Limitations

- Maximum 1000 recipients per bulk send
- Images must be hosted externally (provide URLs)
- HTML content is generated automatically (no custom HTML injection)
- SMTP configuration must be properly set in environment variables

## Environment Variables Required

Make sure these are set in your `.env` file:

```
EMAIL_SMTP_HOST=your-smtp-host
EMAIL_SMTP_PORT=587
EMAIL_SENDER=your-email@example.com
EMAIL_SENDER_PASSWORD=your-email-password
EMAIL_SENDER_NAME=Dassyor
CLIENT_APP_URL=https://app.dassyor.com
APP_NAME=Dassyor
```
