# QuestTrade Trading Bot - Concepts Summary

## Overview
This is a Python-based automated trading bot that monitors stock prices through the QuestTrade API and sends stop-loss alerts when stocks reach specified thresholds. The bot uses an asynchronous architecture with SQLAlchemy for database management and supports multiple notification channels.

## Core Architecture

### 1. Database Layer (`database/`)
The bot uses SQLite with SQLAlchemy ORM for persistence.

#### Database Models (`models.py`)
- **Token Model**: Stores encrypted QuestTrade API tokens
  - Encrypted refresh/access tokens using Fernet encryption
  - API server endpoint
  - Token expiry date for automatic refresh
- **Stock Model**: Tracks monitored stocks
  - Ticker symbol (primary key)
  - Current value, peak value, stop-loss threshold
  - Last notification timestamp
  - Currency support

#### Custom Type Decorators
- **EncryptedToken**: SQLAlchemy type decorator for encrypting sensitive token data
- **Ticker**: Type decorator that automatically converts stock symbols to uppercase

#### Database Management (`db.py`)
- SQLAlchemy engine configuration with SQLite
- Session factory with context manager for transaction safety
- Database initialization utilities

### 2. API Integration (`tracking/`)

#### QTradeAPI Class (`api.py`)
Core API client that handles:
- **Authentication**: Bearer token headers for API requests
- **Stock Symbol Lookup**: Converts ticker symbols to QuestTrade symbol IDs
- **Batch Price Checking**: Efficient bulk price retrieval for tracked stocks
- **Rate Limiting**: Built-in delays to respect API rate limits (20 req/sec)
- **Error Handling**: Retry logic with token refresh on failure

#### Future WebSocket Support (TODO)
- Async WebSocket listener for real-time price updates
- Concurrent data processing with locks for thread safety

### 3. Stock Management (`database/stock_tracker.py`)

#### StockManager Class
Handles stock tracking logic:
- **Stock Addition/Removal**: CRUD operations for tracked stocks
- **Price Monitoring**: Compares current prices against stop-loss thresholds
- **Dynamic Stop-Loss**: Automatically adjusts stop-loss when stocks reach new peaks
- **Alert Queuing**: Maintains list of stocks that need notification
- **Duplicate Prevention**: Only sends one alert per stock per day

#### Stop-Loss Logic
- Stop-loss ratio configurable via environment variables (default: 0.9 = 90%)
- When stock hits new peak: `new_stop_loss = new_peak * stop_loss_ratio`
- Alerts triggered when: `current_price < stop_loss_threshold`

### 4. Authentication & Token Management (`database/token_manager.py`)

#### TokenManager Class
Sophisticated OAuth2 token management:
- **Automatic Refresh**: Checks token expiry on each API call
- **Secure Storage**: Tokens encrypted at rest in database
- **Bootstrap Handling**: Initial token from environment variable
- **Error Recovery**: Handles expired/invalid tokens gracefully

#### Token Lifecycle
1. Initial refresh token from environment variable
2. Exchange for access token + new refresh token
3. Store encrypted in database with expiry
4. Auto-refresh when needed before API calls

### 5. Alert System (`alerts/`)

#### Multi-Channel Architecture
- **BaseAlert**: Abstract base class defining alert interface
- **Pluggable Channels**: Email, Discord webhooks, NTFY push notifications
- **Factory Pattern**: `get_alert_channel()` function for channel instantiation

#### Alert Types
- **Email**: SMTP-based email alerts (Gmail/Outlook support)
- **Discord**: Webhook-based Discord notifications
- **Push**: NTFY service for mobile push notifications

#### Alert Configuration (`handler.py`)
- **AlertConfig**: Dataclass for configuration management
- **Unified Interface**: Single `Alerts` class handles multiple channels
- **Validation**: Built-in validation for each channel's requirements

### 6. Scheduling & Async Operations (`tracking/scheduler.py`)

#### Async Task Management
- **Stock Checking**: Periodic price updates (default: 5 minutes)
- **Alert Dispatch**: Daily alert processing for accumulated notifications
- **Thread Integration**: Uses `asyncio.to_thread()` for sync DB/API operations

#### Scheduling Pattern
```python
async def schedule_checks(api_helper, delay=300):
    while True:
        await asyncio.to_thread(api_helper.get_all_stocks)
        await asyncio.sleep(delay)
```

## Key Design Patterns

### 1. Repository Pattern
- `StockManager` and `TokenManager` act as repositories
- Encapsulate database operations behind clean interfaces
- Handle session management automatically

### 2. Factory Pattern
- `get_alert_channel()` creates alert instances
- Allows runtime selection of notification methods
- Extensible for new alert types

### 3. Context Manager Pattern
- `session_manager()` ensures proper transaction handling
- Automatic commit/rollback on success/failure
- Resource cleanup guaranteed

### 4. Observer Pattern (Implicit)
- Stock price changes trigger alert accumulation
- Batch processing of alerts prevents spam
- Decoupled notification from price checking

## Configuration Management

### Environment Variables (`utils/env_vars.py`)
Required configurations:
- **Authentication**: `refresh_token`, `encryption_key`
- **Email Settings**: `BOT_EMAIL`, `EMAIL_PASSWORD`, `USER_EMAIL`, `PROVIDER`
- **Trading**: `STOP_LOSS` ratio
- **Notifications**: `NTFY_CHANNEL`, `WEB_HOOK_URL`

### Security Considerations
- All sensitive tokens encrypted at rest
- Environment-based configuration
- Strict environment variable validation

## Data Flow

### 1. Initialization Flow
```
main.py → init_db() → create tables
       → QTradeAPI(session_maker)
       → schedule async tasks
```

### 2. Stock Monitoring Flow
```
scheduler → QTradeAPI.get_all_stocks()
         → get_stock_symbol() for each ticker
         → check_stock_info() batch API call
         → StockManager.check_stock() per result
         → update prices + check thresholds
         → queue alerts if needed
```

### 3. Alert Flow
```
scheduler → StockManager.alert_stocks()
         → get queued stocks from database
         → check last_notified timestamps
         → compose alert message
         → send via configured channels
         → update last_notified timestamps
```

## Error Handling Strategies

### 1. Network Resilience
- Retry logic with exponential backoff
- Token refresh on authentication failures
- Rate limiting compliance

### 2. Database Resilience
- Context managers ensure cleanup
- Rollback on exceptions
- Detached instance handling

### 3. Configuration Validation
- Strict environment variable checking
- Runtime validation of alert configurations
- Graceful degradation for missing channels

## Performance Optimizations

### 1. Batch Operations
- Bulk stock price retrieval instead of individual calls
- Single database session per operation
- Async task scheduling

### 2. Caching Strategy
- Tokens cached in memory during session
- Database queries optimized with proper indexing
- Minimal API calls through batching

### 3. Resource Management
- Connection pooling via sessionmaker
- Proper cleanup with context managers
- Memory-efficient async operations

## Testing Architecture (`tests/`)
- Unit tests for database operations
- Alert system testing
- Stock tracking validation
- Mock-based API testing

## Future Enhancements

### 1. WebSocket Implementation
- Real-time price streaming
- Reduced API rate limit pressure
- Lower latency alerts

### 2. User Interface
- Web dashboard for stock management
- Configuration interface
- Historical data visualization

### 3. Advanced Features
- Portfolio integration
- Multiple stop-loss strategies
- Technical indicator support
- Backtesting capabilities

## Key Learnings & Best Practices

### 1. Async/Sync Integration
- Use `asyncio.to_thread()` for blocking operations
- Maintain clean separation between async scheduling and sync business logic
- Proper resource cleanup across async boundaries

### 2. Database Design
- Custom type decorators for business logic
- Proper transaction management
- Encryption for sensitive data

### 3. API Integration
- Rate limiting respect
- Robust error handling
- Token lifecycle management

### 4. Configuration Management
- Environment-based configuration
- Validation at startup
- Secure handling of secrets

This architecture demonstrates a well-structured Python application combining async programming, database ORM, API integration, and multi-channel notifications in a production-ready trading bot.