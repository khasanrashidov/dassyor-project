# Dassyor.com - AI-Powered Startup Validation Platform

A dynamic web platform that empowers entrepreneurs by transforming business ideas into market-validated concepts through intelligent analysis and user-centric design. Built with modern web technologies, the platform features a comprehensive admin dashboard, waitlist system, and AI-powered idea refinement.

![Dassyor Platform](https://dassyor.com/og-image.png)

## 🚀 Features

- **AI-Powered Idea Validation**
  - Instant business idea analysis and refinement
  - Target audience identification
  - Problem statement generation
  - Market validation insights

- **Modern Landing Page**
  - Responsive and mobile-friendly interface
  - Smooth page transitions and animations
  - Interactive sections with clear call-to-actions
  - Progress tracking for idea validation journey

- **Waitlist & Newsletter System**
  - Secure email capture with validation
  - Duplicate prevention with consistent user experience
  - Telegram username integration
  - Automatic success notifications

- **Admin Dashboard**
  - Secure authentication system
  - Comprehensive waitlist management
  - Excel export capabilities
  - User record management
  - Protected routes and API endpoints

## 🛠️ Tech Stack

- **Frontend**
  - React.js with TypeScript
  - Tailwind CSS for styling
  - Shadcn UI components
  - Framer Motion for animations
  - React Query for data fetching
  - Wouter for routing

- **Backend**
  - Express.js server
  - PostgreSQL database
  - Drizzle ORM with PostgreSQL
  - OpenAI integration for AI analysis
  - Express session management
  - Rate limiting for security

## 📁 Project Structure

```
dassyor/
├── client/                 # Frontend React application
│   ├── public/             # Static assets
│   └── src/
│       ├── components/     # UI components
│       │   ├── landing/    # Landing page components
│       │   └── ui/         # Shadcn UI components
│       ├── hooks/          # Custom React hooks
│       ├── lib/            # Utility functions
│       ├── pages/          # Page components
│       │   ├── admin/      # Admin dashboard pages
│       │   └── legal/      # Terms and privacy pages
│       ├── App.tsx         # Main application component
│       └── main.tsx        # Application entry point
│
├── server/                 # Backend Express application
│   ├── db.ts               # Database connection
│   ├── index.ts            # Server entry point
│   ├── routes.ts           # API routes
│   ├── storage.ts          # Data access layer
│   └── vite.ts             # Vite server configuration
│
├── shared/                 # Shared code between client and server
│   └── schema.ts           # Database schema and TypeScript types
│
├── drizzle.config.ts       # Drizzle ORM configuration
├── package.json            # Project dependencies
├── tailwind.config.ts      # Tailwind CSS configuration
└── vite.config.ts          # Vite bundler configuration
```

## 🔧 Development Setup

### Prerequisites

- Node.js (v18+)
- PostgreSQL database
- OpenAI API key (for AI features)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dassyor.git
cd dassyor
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables (create a `.env` file in the project root):
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/dassyor

# Session
SESSION_SECRET=your_secure_session_secret

# OpenAI (for idea validation)
OPENAI_API_KEY=your_openai_api_key

# Admin route (optional, for security)
VITE_ADMIN_ROUTE=your_custom_admin_route
```

4. Initialize the database schema:
```bash
npm run db:push
```

5. Start the development server:
```bash
npm run dev
```

6. Access the application at [http://localhost:5000](http://localhost:5000)

## 🚢 Deployment

### Production Build

1. Create a production build:
```bash
npm run build
```

2. Start the production server:
```bash
npm start
```

### Environment Considerations

For production deployment, ensure these environment variables are properly set:

- `NODE_ENV=production` - Enables production optimizations
- `SESSION_SECRET` - A strong, unique session secret
- `DATABASE_URL` - Your production database connection string
- `OPENAI_API_KEY` - Your OpenAI API key

### Cookie Security

The application uses secure cookie configuration for production:
- `secure: true` - Cookies only sent over HTTPS
- `sameSite: 'none'` - Allows cross-domain cookie use
- `httpOnly: true` - Prevents JavaScript access to cookies

## 🔐 Security Features

- Rate-limited authentication (5 attempts per 15 minutes)
- Secure session management with flexible IP validation
- Admin routes protected by authentication middleware
- Password hashing with bcrypt
- Input validation with Zod schemas
- HTTPS agent configuration for API requests
- XSS protection through proper data handling

## 🧪 Testing

Run the test suite:
```bash
npm test
```

## 🌐 Routes and Pages

### Client Routes
- `/` - Main landing page
- `/validate` - Idea validation page
- `/terms` - Terms of Service
- `/privacy` - Privacy Policy
- `/admin/login` - Admin login page
- `/admin/dashboard` - Admin dashboard (protected)

### API Endpoints
- `POST /api/newsletter` - Join newsletter/waitlist
- `POST /api/submit-idea` - Submit idea for validation
- `POST /api/refine-idea` - AI-powered idea refinement
- `POST /api/{adminRoute}` - Admin authentication
- `GET /api/admin/newsletters` - Get all newsletter subscribers
- `DELETE /api/admin/newsletters/:id` - Delete a newsletter entry
- `GET /api/admin/newsletters/export` - Export subscribers to Excel

## 👥 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style

- Follow TypeScript best practices
- Use ESLint and Prettier for code formatting
- Write meaningful commit messages
- Update documentation when changing functionality

## 📞 Contact

For inquiries, support, or feedback:
- Telegram: [@dassyorcom](https://t.me/dassyorcom)
- Instagram: [@dassyorcom](https://www.instagram.com/dassyorcom/)
- LinkedIn: [dassyorcom](https://www.linkedin.com/company/dassyorcom)
- X (Twitter): [@dassyor](https://x.com/dassyor)

## 📄 License

All rights reserved © 2024 dassyor.com

---

Built with ❤️ for entrepreneurs and innovators
