# Gateway Hub - Frontend (TypeScript + React)

A modern, type-safe URL Shortener SaaS frontend built with TypeScript and React.

## 🚀 Features

- **TypeScript Support**: Full type safety across the application
- **React Hooks**: Modern functional components with custom hooks
- **Context API**: State management for authentication and links
- **Responsive Design**: Mobile-first approach with CSS modules
- **Component-based Architecture**: Reusable, maintainable components
- **API Client**: Centralized API service with axios
- **Authentication**: Login, registration, and session management
- **User Dashboard**: Manage short links with real-time updates

## 📁 Project Structure

```
src/
├── types/              # TypeScript interfaces
├── services/           # API client and external services
├── context/            # React Context providers
├── hooks/              # Custom React hooks
├── components/         # Reusable React components
├── pages/              # Page components
├── styles/             # Global and CSS variables
├── App.tsx             # Main app component
└── index.tsx           # Entry point

public/
└── index.html          # HTML template
```

## 🛠 Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env.local
   ```

3. **Update API URL** in `.env.local`:
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   ```

## 🏃 Running the Application

**Development mode:**
```bash
npm start
```

The app will start on `http://localhost:3000`

**Build for production:**
```bash
npm run build
```

**Run tests:**
```bash
npm test
```

## 📦 Key Dependencies

- **react**: UI library
- **react-router-dom**: Client-side routing
- **axios**: HTTP client
- **TypeScript**: Type safety

## 🔧 Configuration

### API Client (`src/services/api.ts`)

The API client is pre-configured with:
- Base URL from environment variables
- Automatic Bearer token injection
- Request/response interceptors
- 401 error handling

### Context Providers

- **AuthContext**: User authentication state
- **LinksContext**: Short links management

### Custom Hooks

- `useAuth()`: Access authentication context
- `useLinks()`: Access links context

## 🎨 Styling

The project uses:
- **CSS Modules** for component-specific styles
- **CSS Variables** for theming
- **Mobile-first** responsive design

### Key Colors

- Primary: `#667eea` (Purple)
- Secondary: `#764ba2` (Dark Purple)
- Success: `#10b981` (Green)
- Error: `#ef4444` (Red)

## 🔐 Authentication Flow

1. User registers/logs in
2. API returns JWT token and user data
3. Token is stored in localStorage
4. Token is automatically attached to all API requests
5. On 401 error, user is redirected to login

## 📝 Component Documentation

### Header
Main navigation component with user info and logout button.

### LinkForm
Form for creating new short links with free tier validation.

### LinkTable
Displays user's short links with copy and delete actions.

### Pages
- **Home**: Landing page with features and pricing
- **Login**: User login form
- **Register**: User registration form
- **Dashboard**: Main user dashboard
- **NotFound**: 404 error page

## 🚀 Deployment

### Build & Deploy to Vercel

```bash
npm run build
vercel deploy
```

### Build & Deploy to Netlify

```bash
npm run build
netlify deploy --prod --dir=build
```

### Environment Variables for Production

Set these in your deployment platform:
```
REACT_APP_API_URL=https://api.yourdomain.com
```

## 🐛 Troubleshooting

**CORS errors:**
- Ensure backend API has proper CORS headers configured
- Update `REACT_APP_API_URL` to match backend URL

**Authentication not working:**
- Check localStorage for token: `miniurl_token`
- Verify API endpoints return proper `AuthResponse` format

**Styling issues:**
- Clear browser cache
- Ensure CSS Modules are imported correctly

## 📖 API Integration

The frontend expects the backend to provide these endpoints:

```
POST   /auth/register      - Register new user
POST   /auth/login         - Login user
POST   /auth/logout        - Logout user
GET    /user/stats         - Get user statistics
POST   /user/upgrade       - Upgrade to premium
GET    /links              - Get all user links
POST   /links/create       - Create new link
DELETE /links/:code        - Delete link
GET    /links/:code/analytics - Get link analytics
GET    /redirect/:code     - Redirect to target URL
```

## 📄 License

MIT

## 👨‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
