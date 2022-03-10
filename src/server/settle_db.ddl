CREATE TABLE groups (
  group_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE keys (
    key_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_n BLOB,  -- 256bit modulus
    key_e BLOB   -- 4 bit pub exp
);

CREATE TABLE group_link (
    group_link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    usr_id INTEGER,

    FOREIGN KEY(group_id) REFERENCES groups(group_id),
    FOREIGN KEY(usr_id) REFERENCES users(usr_id)
);

CREATE TABLE users (
  usr_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT,
  password TEXT, --will be bytes stores as txt
  key_id INTEGER,

  FOREIGN KEY(key_id) REFERENCES keys(key_id)

);

CREATE TABLE pairs (
    pair_id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id INTEGER,
    dest_id INTEGER,

    FOREIGN KEY(src_id) REFERENCES users(usr_id),
    FOREIGN KEY(dest_id) REFERENCES users(usr_id)
);


CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    amount INTEGER,  -- store in pennies
    src_key INTEGER,
    dest_key INTEGER,
    reference TEXT,
    time_of_creation TEXT,
    src_sig BLOB,
    dest_sig BLOB,
    settled INTEGER NOT NULL DEFAULT 0,-- 0 or 1

    FOREIGN KEY(pair_id) REFERENCES pairs(pair_id),
    FOREIGN KEY(group_id) REFERENCES groups(group_id)
);

