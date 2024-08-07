

-- CREATE EXTENSION

CREATE EXTENSION "uuid-ossp";


-- public.devices definition

-- Drop table

-- DROP TABLE public.devices;

CREATE TABLE public.devices (
	device_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	reference varchar NOT NULL,
	timer_loop int4 NULL,
	measurement varchar NULL,
	file varchar NULL,
	gateway varchar NULL,
	available bool NULL,
	last_access timestamptz NULL,
	CONSTRAINT devices_pk PRIMARY KEY (device_id),
	CONSTRAINT devices_reference_key UNIQUE (reference)
);

-- public.channels definition

-- Drop table

-- DROP TABLE public.channels;

CREATE TABLE public.channels (
	channel_id uuid NOT NULL DEFAULT uuid_generate_v4(),
	device_id uuid NOT NULL,
	channel int4 NULL,
	unit varchar NULL,
	item varchar NOT NULL,
	constant numeric NULL,
	CONSTRAINT channels_pk PRIMARY KEY (channel_id)
);


-- public.channels foreign keys

ALTER TABLE public.channels ADD CONSTRAINT channels_fk FOREIGN KEY (device_id) REFERENCES public.devices(device_id);

-- public.sensor_data definition

-- Drop table

-- DROP TABLE public.sensor_data;

CREATE TABLE public.sensor_data (
	"time" timestamptz NOT NULL,
	channel_id uuid NULL,
	data_value float8 NULL,
	measurement varchar NULL
);


-- public.sensor_data foreign keys

ALTER TABLE public.sensor_data ADD CONSTRAINT sensor_data_channel_id_fkey FOREIGN KEY (channel_id) REFERENCES public.channels(channel_id);


-- public.alerts definition

-- Drop table

-- DROP TABLE public.alerts;

CREATE TABLE public.alerts (
	device_id uuid NOT NULL,
	alert varchar NULL,
	"time" timestamptz NULL
);


ALTER TABLE public.channels ADD COLUMN writable BOOLEAN DEFAULT FALSE;