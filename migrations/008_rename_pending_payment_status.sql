-- Rename status value: pending_payment → pending_confirmation
UPDATE bookings
SET status = 'pending_confirmation'
WHERE status = 'pending_payment';

ALTER TABLE bookings
    ALTER COLUMN status SET DEFAULT 'pending_confirmation';
