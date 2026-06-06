import { query } from './client';

/**
 * Example analytical queries demonstrating DuckDB capabilities
 */

export interface EventStats {
  event_type: string;
  count: number;
  unique_users: number;
}

export interface UserActivity {
  user_id: string;
  event_count: number;
  last_event: string;
  first_event: string;
}

export interface TimeSeriesData {
  date: string;
  hour: number;
  event_count: number;
}

/**
 * Get event statistics grouped by event type
 */
export async function getEventStats(): Promise<EventStats[]> {
  const sql = `
    SELECT
      event_type,
      COUNT(*) as count,
      COUNT(DISTINCT user_id) as unique_users
    FROM events
    GROUP BY event_type
    ORDER BY count DESC
  `;
  return query<EventStats[]>(sql);
}

/**
 * Get user activity summary
 */
export async function getUserActivity(userId?: string): Promise<UserActivity[]> {
  const whereClause = userId ? `WHERE user_id = '${userId}'` : '';
  const sql = `
    SELECT
      user_id,
      COUNT(*) as event_count,
      MAX(timestamp) as last_event,
      MIN(timestamp) as first_event
    FROM events
    ${whereClause}
    GROUP BY user_id
    ORDER BY event_count DESC
    LIMIT 100
  `;
  return query<UserActivity[]>(sql);
}

/**
 * Get time series data for events
 */
export async function getTimeSeriesData(days: number = 7): Promise<TimeSeriesData[]> {
  const sql = `
    SELECT
      DATE_TRUNC('day', timestamp) as date,
      HOUR(timestamp) as hour,
      COUNT(*) as event_count
    FROM events
    WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL '${days} days'
    GROUP BY date, hour
    ORDER BY date, hour
  `;
  return query<TimeSeriesData[]>(sql);
}

/**
 * Get top users by event count
 */
export async function getTopUsers(limit: number = 10): Promise<UserActivity[]> {
  const sql = `
    SELECT
      e.user_id,
      u.username,
      u.email,
      COUNT(*) as event_count,
      MAX(e.timestamp) as last_event,
      MIN(e.timestamp) as first_event
    FROM events e
    LEFT JOIN users u ON e.user_id = u.user_id
    GROUP BY e.user_id, u.username, u.email
    ORDER BY event_count DESC
    LIMIT ${limit}
  `;
  return query<UserActivity[]>(sql);
}

/**
 * Analyze JSON event data
 */
export async function analyzeEventData(eventType: string): Promise<any[]> {
  const sql = `
    SELECT
      event_type,
      COUNT(*) as count,
      json_extract(event_data, '$.category') as category,
      json_extract(event_data, '$.value') as avg_value
    FROM events
    WHERE event_type = '${eventType}'
    GROUP BY event_type, category
    ORDER BY count DESC
  `;
  return query(sql);
}

/**
 * Insert sample event data
 */
export async function insertEvent(
  userId: string,
  eventType: string,
  eventData: Record<string, any>
): Promise<void> {
  const eventId = `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const sql = `
    INSERT INTO events (event_id, user_id, event_type, event_data)
    VALUES (
      '${eventId}',
      '${userId}',
      '${eventType}',
      '${JSON.stringify(eventData)}'::JSON
    )
  `;
  await query(sql);
}

/**
 * Insert sample user data
 */
export async function insertUser(
  userId: string,
  username: string,
  email: string
): Promise<void> {
  const sql = `
    INSERT INTO users (user_id, username, email)
    VALUES ('${userId}', '${username}', '${email}')
    ON CONFLICT (user_id) DO NOTHING
  `;
  await query(sql);
}

/**
 * Query remote Parquet files (example with public datasets)
 */
export async function queryRemoteParquet(url: string): Promise<any[]> {
  const sql = `
    SELECT *
    FROM read_parquet('${url}')
    LIMIT 100
  `;
  return query(sql);
}

/**
 * Advanced aggregation: cohort analysis
 */
export async function getCohortAnalysis(): Promise<any[]> {
  const sql = `
    WITH user_first_event AS (
      SELECT
        user_id,
        DATE_TRUNC('week', MIN(timestamp)) as cohort_week
      FROM events
      GROUP BY user_id
    ),
    user_events AS (
      SELECT
        e.user_id,
        ufe.cohort_week,
        DATE_TRUNC('week', e.timestamp) as event_week,
        COUNT(*) as event_count
      FROM events e
      JOIN user_first_event ufe ON e.user_id = ufe.user_id
      GROUP BY e.user_id, ufe.cohort_week, event_week
    )
    SELECT
      cohort_week,
      event_week,
      COUNT(DISTINCT user_id) as active_users,
      SUM(event_count) as total_events
    FROM user_events
    GROUP BY cohort_week, event_week
    ORDER BY cohort_week, event_week
  `;
  return query(sql);
}
