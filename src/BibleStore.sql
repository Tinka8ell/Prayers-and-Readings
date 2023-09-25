CREATE TABLE `version` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `abbreviation` LONGTEXT UNIQUE NOT NULL,
  `name` VARCHAR(255) NOT NULL
);

CREATE TABLE `book` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `extenedabbreviation` VARCHAR(255) UNIQUE NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `total` INTEGER NOT NULL,
  `version` INTEGER NOT NULL
);

CREATE INDEX `idx_book__version` ON `book` (`version`);

ALTER TABLE `book` ADD CONSTRAINT `fk_book__version` FOREIGN KEY (`version`) REFERENCES `version` (`id`) ON DELETE CASCADE;

CREATE TABLE `chapter` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `number` INTEGER NOT NULL,
  `verses` INTEGER NOT NULL,
  `book` INTEGER NOT NULL
);

CREATE INDEX `idx_chapter__book` ON `chapter` (`book`);

ALTER TABLE `chapter` ADD CONSTRAINT `fk_chapter__book` FOREIGN KEY (`book`) REFERENCES `book` (`id`) ON DELETE CASCADE;

CREATE TABLE `verse` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `number` INTEGER NOT NULL,
  `last` INTEGER,
  `content` VARCHAR(255) NOT NULL,
  `chapter` INTEGER NOT NULL
);

CREATE INDEX `idx_verse__chapter` ON `verse` (`chapter`);

ALTER TABLE `verse` ADD CONSTRAINT `fk_verse__chapter` FOREIGN KEY (`chapter`) REFERENCES `chapter` (`id`) ON DELETE CASCADE;

CREATE TABLE `lookup` (
  `id` INTEGER PRIMARY KEY AUTO_INCREMENT,
  `number` INTEGER NOT NULL,
  `chapter` INTEGER NOT NULL,
  `verse` INTEGER NOT NULL
);

CREATE INDEX `idx_lookup__chapter` ON `lookup` (`chapter`);

CREATE INDEX `idx_lookup__verse` ON `lookup` (`verse`);

ALTER TABLE `lookup` ADD CONSTRAINT `fk_lookup__chapter` FOREIGN KEY (`chapter`) REFERENCES `chapter` (`id`) ON DELETE CASCADE;

ALTER TABLE `lookup` ADD CONSTRAINT `fk_lookup__verse` FOREIGN KEY (`verse`) REFERENCES `verse` (`id`) ON DELETE CASCADE
