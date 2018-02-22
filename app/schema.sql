DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS slides;
DROP TABLE IF EXISTS user_to_slides;
DROP TABLE IF EXISTS annotations;
CREATE TABLE users (title VARCHAR(10), fname VARCHAR(20), lname VARCHAR(20), email VARCHAR(50), date_joined DATETIME, institute VARCHAR(50), country VARCHAR(25), password VARCHAR(50), id INTEGER PRIMARY KEY);
CREATE TABLE slides (name VARCHAR(50), location VARCHAR(50), type VARCHAR(25), case_num VARCHAR(50), consultant VARCHAR(50), clinic_details TEXT, prov_diag TEXT, dateuploaded DATETIME, viewable INTEGER, uploader_id INTEGER, id INTEGER PRIMARY KEY, FOREIGN KEY(uploader_id) REFERENCES users(id));
CREATE TABLE user_to_slides (user_id INTEGER, slide_id INTEGER, accessed DATETIME, FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (slide_id) REFERENCES slides(id));
CREATE TABLE annotations (name VARCHAR(50), description TEXT, colour TEXT, points TEXT, thumbnail TEXT, annotator_id INTEGER, slide_id INTEGER, id INTEGER PRIMARY KEY , FOREIGN KEY (annotator_id) REFERENCES users(id), FOREIGN KEY (slide_id) REFERENCES slides(id));
CREATE TABLE permissions (slide_id INTEGER, user_id INTEGER, FOREIGN KEY (slide_id) REFERENCES slides(id), FOREIGN KEY (user_id) REFERENCES users(id));