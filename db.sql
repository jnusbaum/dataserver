CREATE TABLE "zone" (
  "name" TEXT PRIMARY KEY,
  "description" VARCHAR(512)
);

CREATE TABLE "sensor" (
  "name" TEXT PRIMARY KEY,
  "type" VARCHAR(8) NOT NULL,
  "address" VARCHAR(128),
  "description" VARCHAR(512),
  "zone" TEXT
);

CREATE INDEX "idx_sensor__zone" ON "sensor" ("zone");

ALTER TABLE "sensor" ADD CONSTRAINT "fk_sensor__zone" FOREIGN KEY ("zone") REFERENCES "zone" ("name") ON DELETE SET NULL;

CREATE TABLE "sensordata" (
  "id" SERIAL PRIMARY KEY,
  "sensor" TEXT NOT NULL,
  "timestamp" TIMESTAMP NOT NULL,
  "value_real" DECIMAL(12, 2) NOT NULL,
  "original_value" DECIMAL(12, 2),
);

CREATE INDEX "idx_sensordata__sensor_timestamp" ON "sensordata" ("sensor", "timestamp");

ALTER TABLE "sensordata" ADD CONSTRAINT "fk_sensordata__sensor" FOREIGN KEY ("sensor") REFERENCES "sensor" ("name") ON DELETE CASCADE