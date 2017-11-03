INSERT INTO users VALUES ('Dr', 'Bob', 'Smith', 'bsmith@dr.com', '10-10-2017', 'hospital', 'UK', '$5$rounds=535000$5ZYgtqjotYA97k/A$LipkTSaEV35d9Y./FXE7krWTEycVB13m6gBaVr8TJY5', NULL );
INSERT INTO users VALUES ('Miss', 'Eve', 'Jones', 'ejones@dr.com', '10-09-2017', 'hospital', 'UK', '$5$rounds=535000$5ZYgtqjotYA97k/A$LipkTSaEV35d9Y./FXE7krWTEycVB13m6gBaVr8TJY5', NULL );
INSERT INTO users VALUES ('Mr', 'Alex', 'Smith', 'asmith@dr.com', '05-10-2017', 'university', 'UK', '$5$rounds=535000$5ZYgtqjotYA97k/A$LipkTSaEV35d9Y./FXE7krWTEycVB13m6gBaVr8TJY5', NULL );
INSERT INTO users VALUES ('Mrs', 'Christine', 'Trott', 'ctrott@dr.com', '25-09-2017', 'research facility', 'UK', '$5$rounds=535000$5ZYgtqjotYA97k/A$LipkTSaEV35d9Y./FXE7krWTEycVB13m6gBaVr8TJY5', NULL );
INSERT INTO users VALUES ('Miss', 'Emma', 'Long', 'elong@dr.com', '13-09-2017', 'hospital', 'UK', '$5$rounds=535000$5ZYgtqjotYA97k/A$LipkTSaEV35d9Y./FXE7krWTEycVB13m6gBaVr8TJY5', NULL );

INSERT INTO slides VALUES ('slide_1', 'static/img/thumb.jpg', 'oral', '20-10-2017', 1, NULL);
INSERT INTO slides VALUES ('slide_2', 'slide_2.folder', 'oral', '21-10-2017', 2, NULL);
INSERT INTO slides VALUES ('slide_3', 'slide_3.folder', 'oral', '22-10-2017', 3, NULL);
INSERT INTO slides VALUES ('slide_4', 'slide_4.folder', 'stomach', '23-10-2017', 2, NULL);
INSERT INTO slides VALUES ('slide_5', 'slide_5.folder', 'stomach', '24-10-2017', 3, NULL);
INSERT INTO slides VALUES ('slide_6', 'slide_6.folder', 'stomach', '25-10-2017', 4, NULL);
INSERT INTO slides VALUES ('slide_7', 'slide_7.folder', 'chest', '26-10-2017', 3, NULL);
INSERT INTO slides VALUES ('slide_8', 'slide_8.folder', 'chest', '27-10-2017', 4, NULL);
INSERT INTO slides VALUES ('slide_9', 'slide_9.folder', 'chest', '28-10-2017', 5, NULL);

INSERT INTO user_to_slides VALUES (1, 1, '21-10-2017');
INSERT INTO user_to_slides VALUES (1, 2, '22-10-2017');
INSERT INTO user_to_slides VALUES (1, 4, '23-10-2017');
INSERT INTO user_to_slides VALUES (1, 5, '24-10-2017');
INSERT INTO user_to_slides VALUES (1, 9, '25-10-2017');
INSERT INTO user_to_slides VALUES (1, 7, '26-10-2017');
INSERT INTO user_to_slides VALUES (1, 8, '27-10-2017');
INSERT INTO user_to_slides VALUES (2, 1, '28-10-2017');
INSERT INTO user_to_slides VALUES (3, 1, '29-10-2017');
