# Project Structure Overview

## Directory Layout

```
src/
├── types/
│   └── index.ts                 # TypeScript interfaces and types
│
├── services/
│   └── api.ts                   # API client with axios
│
├── context/
│   ├── AuthContext.tsx          # Authentication state management
│   └── LinksContext.tsx         # Links state management
│
├── hooks/
│   ├── useAuth.ts               # Hook for auth context
│   └── useLinks.ts              # Hook for links context
│
├── components/
│   ├── Header.tsx               # Navigation header
│   ├── Header.module.css
│   ├── LinkForm.tsx             # Form to create short links
│   ├── LinkForm.module.css
│   ├── LinkTable.tsx            # Table displaying user's links
│   └── LinkTable.module.css
│
├── pages/
│   ├── Home.tsx                 # Landing page
│   ├── Login.tsx                # Login page
│   ├── Register.tsx             # Registration page
│   ├── Dashboard.tsx            # Main user dashboard
│   └── NotFound.tsx             # 404 error page
│
├── styles/
│   ├── variables.css            # CSS custom properties
│   └── globals.css              # Global styles
│
├── App.tsx                      # Root application component
├── index.tsx                    # React entry point
└── config.ts                    # Application constants

public/
└── index.html                   # HTML template
```

## File Descriptions

### Types (`src/types/index.ts`)
- `User`: User profile information
- `ShortLink`: Short URL link data
- `UserStats`: User statistics and limits
- `AuthResponse`: API authentication response
- `AuthContextType`: Authentication context interface
- `LinksContextType`: Links context interface

### Services (`src/services/api.ts`)
- Centralized API client using axios
- Automatic token injection in headers
- Request/response interceptors
- 401 error handling with redirect to login
- All endpoints for auth, users, and links

### Context Providers
- **AuthContext**: Manages user authentication state
- **LinksContext**: Manages short links and user stats

### Custom Hooks
- `useAuth()`: Access authentication context
- `useLinks()`: Access links context

### Components
- **Header**: Top navigation with user info and logout
- **LinkForm**: Form for creating new short links
- **LinkTable**: Displays user's links with copy/delete actions

### Pages
- **Home**: Landing page with features and signup/login links
- **Login**: User login form
- **Register**: User registration form
- **Dashboard**: Main dashboard with stats, form, and links table
- **NotFound**: 404 error page

### Styles
- CSS Modules for component-specific styling
- Global CSS with CSS variables for theming
- Mobile-first responsive design

## Data Flow

1. User logs in → AuthContext stores user and token
2. Token is automatically attached to all API requests
3. User can create, view, and delete short links
4. LinksContext manages links state and syncs with backend
5. Stats are fetched and displayed on dashboard

## Key Features

✅ Type-safe TypeScript throughout
✅ Context API for state management
✅ Custom React hooks for context consumption
✅ API client with interceptors
✅ Responsive mobile-first design
✅ CSS Modules for styling
✅ Authentication with JWT tokens
✅ Free and Premium tier support
✅ Error handling and loading states
✅ Real-time stats and analytics

## Environment Variables

Create `.env.local` in the project root:

```env
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_CUSTOM_DOMAINS=false
```

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env.local` with API URL

3. Start development server:
   ```bash
   npm start
   ```

4. Build for production:
   ```bash
   npm run build
   ```

## API Integration Points

The frontend connects to these backend endpoints:

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `GET /user/stats` - Get user statistics
- `POST /user/upgrade` - Upgrade to premium
- `GET /links` - Get all user links
- `POST /links/create` - Create new short link
- `DELETE /links/:code` - Delete a link
- `GET /links/:code/analytics` - Get link analytics
- `GET /redirect/:code` - Redirect to target URL

## Authentication Flow

1. User enters credentials on login/register page
2. Frontend sends request to API
3. API returns user data and JWT token
4. Token is stored in localStorage
5. Token is attached to all subsequent requests
6. On 401 error, user is redirected to login
7. On logout, token is removed from storage

## Styling System

The project uses CSS variables for consistent styling:

```css
--primary: #667eea (Main brand color)
--secondary: #764ba2 (Secondary color)
--success: #10b981 (Success state)
--error: #ef4444 (Error state)
--warning: #f59e0b (Warning state)
```

All colors can be customized in `src/styles/variables.css`.
