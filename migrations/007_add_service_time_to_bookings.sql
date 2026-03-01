ALTER TABLE bookings
    ADD COLUMN IF NOT EXISTS service_time TIME;
