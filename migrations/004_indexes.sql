CREATE INDEX IF NOT EXISTS idx_bookings_status        ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_service_date  ON bookings(service_date);
CREATE INDEX IF NOT EXISTS idx_bookings_email         ON bookings(email);
CREATE INDEX IF NOT EXISTS idx_service_areas_postcode ON service_areas(postcode);
