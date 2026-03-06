-- Enable UUID generation for users.id.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create users table.
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid VARCHAR(128) UNIQUE,
    email TEXT,
    display_name TEXT,
    photo_url TEXT,
    provider TEXT CHECK (provider IN ('google.com', 'apple.com') OR provider IS NULL),
    last_sign_in_at TIMESTAMP,
    initial_prompt TEXT NOT NULL,
    enhanced_profile TEXT,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create chat message history table.
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    role VARCHAR(20),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create shown content deduplication table.
CREATE TABLE IF NOT EXISTS shown_content (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    content_url TEXT NOT NULL,
    shown_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, content_url)
);

-- Create content cache table.
CREATE TABLE IF NOT EXISTS content_cache (
    id BIGSERIAL PRIMARY KEY,
    query_hash TEXT UNIQUE,
    results JSONB,
    cached_at TIMESTAMP DEFAULT NOW()
);

-- Create lookup indexes.
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON users(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_messages(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_shown_content ON shown_content(user_id, shown_at);

