-- Seed major world regions
INSERT INTO regions (name, code, level, latitude, longitude, population) VALUES
-- World
('World', 'WORLD', 'world', 0, 0, 8000000000),

-- Continents
('North America', 'NA', 'continent', 54.5260, -105.2551, 579000000),
('South America', 'SA', 'continent', -8.7832, -55.4915, 430000000),
('Europe', 'EU', 'continent', 54.5260, 15.2551, 748000000),
('Asia', 'AS', 'continent', 34.0479, 100.6197, 4600000000),
('Africa', 'AF', 'continent', -8.7832, 34.5085, 1340000000),
('Oceania', 'OC', 'continent', -22.7359, 140.0188, 43000000),

-- Major Countries
('United States', 'USA', 'country', 37.0902, -95.7129, 331000000),
('China', 'CHN', 'country', 35.8617, 104.1954, 1440000000),
('India', 'IND', 'country', 20.5937, 78.9629, 1380000000),
('Brazil', 'BRA', 'country', -14.2350, -51.9253, 213000000),
('United Kingdom', 'GBR', 'country', 55.3781, -3.4360, 68000000),
('Germany', 'DEU', 'country', 51.1657, 10.4515, 83000000),
('France', 'FRA', 'country', 46.2276, 2.2137, 65000000),
('Italy', 'ITA', 'country', 41.8719, 12.5674, 60000000),
('Spain', 'ESP', 'country', 40.4637, -3.7492, 47000000),
('Canada', 'CAN', 'country', 56.1304, -106.3468, 38000000),
('Mexico', 'MEX', 'country', 23.6345, -102.5528, 129000000),
('Japan', 'JPN', 'country', 36.2048, 138.2529, 126000000),
('South Korea', 'KOR', 'country', 35.9078, 127.7669, 52000000),
('Australia', 'AUS', 'country', -25.2744, 133.7751, 26000000),
('Nigeria', 'NGA', 'country', 9.0820, 8.6753, 206000000),
('South Africa', 'ZAF', 'country', -30.5595, 22.9375, 60000000),
('Kenya', 'KEN', 'country', -0.0236, 37.9062, 54000000),
('Egypt', 'EGY', 'country', 26.8206, 30.8025, 102000000),
('Indonesia', 'IDN', 'country', -0.7893, 113.9213, 274000000),
('Thailand', 'THA', 'country', 15.8700, 100.9925, 70000000),
('Vietnam', 'VNM', 'country', 14.0583, 108.2772, 98000000),
('Philippines', 'PHL', 'country', 12.8797, 121.7740, 110000000),
('Russia', 'RUS', 'country', 61.5240, 105.3188, 146000000),
('Argentina', 'ARG', 'country', -38.4161, -63.6167, 45000000),
('Colombia', 'COL', 'country', 4.5709, -74.2973, 51000000);

-- Set parent relationships (continents to world)
UPDATE regions SET parent_id = (SELECT id FROM regions WHERE code = 'WORLD')
WHERE level = 'continent';

-- Set parent relationships (countries to continents)
UPDATE regions SET parent_id = (SELECT id FROM regions WHERE code = 'NA')
WHERE code IN ('USA', 'CAN', 'MEX');

UPDATE regions SET parent_id = (SELECT id FROM regions WHERE code = 'SA')
WHERE code IN ('BRA', 'ARG', 'COL');

UPDATE regions SET parent_id = (SELECT id FROM regions WHERE code = 'EU')
WHERE code IN ('GBR', 'DEU', 'FRA', 'ITA', 'ESP', 'RUS');

UPDATE regions SET parent_id = (SELECT id FROM regions WHERE code = 'AS')
WHERE code IN ('CHN', 'IND', 'JPN', 'KOR', 'IDN', 'THA', 'VNM', 'PHL');

UPDATE regions SET parent_id = (SELECT id FROM regions WHERE code = 'AF')
WHERE code IN ('NGA', 'ZAF', 'KEN', 'EGY');

UPDATE regions SET parent_id = (SELECT id FROM regions WHERE code = 'OC')
WHERE code IN ('AUS');
