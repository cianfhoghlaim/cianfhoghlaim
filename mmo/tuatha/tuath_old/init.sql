-- Crypteolas Database Initialization
-- Creates schema for Better Auth and payment tracking

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Better Auth tables will be created by Drizzle migrations
-- This file provides any additional initialization needed

-- Create indexes for performance (if not handled by Drizzle)
-- These are safe to run even if tables don't exist yet

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE crypteolas TO crypteolas;
