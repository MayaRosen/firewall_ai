-- AI Firewall Database Schema
-- PostgreSQL 15+

-- Drop existing tables (for clean initialization)
DROP TABLE IF EXISTS connections CASCADE;
DROP TABLE IF EXISTS policies CASCADE;

-- Policies Table
CREATE TABLE policies (
    policy_id VARCHAR(100) PRIMARY KEY,
    conditions JSONB NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('allow', 'block', 'alert')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster policy retrieval
CREATE INDEX idx_policies_action ON policies(action);

-- Connections Table
CREATE TABLE connections (
    connection_id VARCHAR(100) PRIMARY KEY,
    source_ip INET NOT NULL,
    destination_ip INET NOT NULL,
    destination_port INTEGER NOT NULL CHECK (destination_port BETWEEN 0 AND 65535),
    protocol VARCHAR(10) NOT NULL CHECK (protocol IN ('TCP', 'UDP')),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    decision VARCHAR(20) NOT NULL CHECK (decision IN ('allow', 'block', 'alert', 'no-match')),
    anomaly_score NUMERIC(3, 2) NOT NULL CHECK (anomaly_score BETWEEN 0 AND 1),
    matched_policy VARCHAR(100),
    evaluated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matched_policy) REFERENCES policies(policy_id) ON DELETE SET NULL
);

-- Indexes for common query patterns
CREATE INDEX idx_connections_source_ip ON connections(source_ip);
CREATE INDEX idx_connections_destination_ip ON connections(destination_ip);
CREATE INDEX idx_connections_destination_port ON connections(destination_port);
CREATE INDEX idx_connections_decision ON connections(decision);
CREATE INDEX idx_connections_evaluated_at ON connections(evaluated_at DESC);
CREATE INDEX idx_connections_matched_policy ON connections(matched_policy);

-- Composite index for time-series queries
CREATE INDEX idx_connections_timestamp_decision ON connections(timestamp DESC, decision);

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at for policies
CREATE TRIGGER update_policies_updated_at
    BEFORE UPDATE ON policies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE policies IS 'Security policies for connection evaluation';
COMMENT ON TABLE connections IS 'Network connection evaluation history';
COMMENT ON COLUMN policies.conditions IS 'JSON array of policy conditions';
COMMENT ON COLUMN connections.anomaly_score IS 'AI-calculated anomaly score (0.0 to 1.0)';
