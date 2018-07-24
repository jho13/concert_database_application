CREATE TABLE building (
	id int AUTO_INCREMENT,
	name varchar(200),
    location varchar(200),
    capacity int CHECK (capacity > 0),
    assigned boolean,
    PRIMARY KEY (id)
);

CREATE TABLE performance (
	id int AUTO_INCREMENT,
    name varchar(200),
    type varchar(200),
    price int CHECK (price > 0),
    booked int DEFAULT 0,
    building_id int,
    PRIMARY KEY (id),
    FOREIGN KEY (building_id) REFERENCES building(id) ON DELETE SET NULL
);

CREATE TABLE audience (
	id int AUTO_INCREMENT,
    name varchar(200),
    gender char(1) CHECK (gender = 'M' or gender = 'F'),
    age int CHECK (age >= 0),
    PRIMARY KEY(id)
);

CREATE TABLE seat (
	seat_number int,
    performance_id int NOT NULL,
    audience_id int,
    PRIMARY KEY (seat_number, performance_id),
    FOREIGN KEY (performance_id) REFERENCES performance(id) ON DELETE CASCADE,
    FOREIGN KEY (audience_id) REFERENCES audience(id) ON DELETE SET NULL
);