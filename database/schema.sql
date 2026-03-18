CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    goal VARCHAR(50),
    total_budget DECIMAL(12,2),
    daily_budget DECIMAL(12,2),
    start_date DATE,
    end_date DATE,
    brief JSONB,
    platform_ids JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE creatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    type VARCHAR(50),
    platform VARCHAR(50),
    content JSONB,
    performance JSONB,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    platform VARCHAR(50),
    date DATE,
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    spend DECIMAL(12,2) DEFAULT 0,
    conversions INT DEFAULT 0,
    revenue DECIMAL(12,2) DEFAULT 0,
    ctr DECIMAL(6,4),
    cpc DECIMAL(10,4),
    roas DECIMAL(8,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ai_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
    type VARCHAR(50),
    content TEXT,
    severity VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_campaign_date ON metrics(campaign_id, date);
CREATE INDEX idx_creatives_campaign ON creatives(campaign_id);
CREATE INDEX idx_insights_campaign ON ai_insights(campaign_id);
