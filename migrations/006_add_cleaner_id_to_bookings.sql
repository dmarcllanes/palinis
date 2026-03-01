ALTER TABLE bookings
    ADD COLUMN IF NOT EXISTS cleaner_id UUID REFERENCES cleaners(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_bookings_cleaner_id ON bookings(cleaner_id);
