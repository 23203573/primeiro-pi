-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema lalumaredb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema lalumaredb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `lalumaredb` DEFAULT CHARACTER SET utf8 ;
USE `lalumaredb` ;

-- -----------------------------------------------------
-- Table `lalumaredb`.`cliente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `lalumaredb`.`cliente` (
  `id_cliente` VARCHAR(36) NOT NULL,
  `nome` VARCHAR(45) NOT NULL,
  `telefone` VARCHAR(45) NOT NULL,
  `endereco` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id_cliente`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `lalumaredb`.`funcionario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `lalumaredb`.`funcionario` (
  `id_funcionario` VARCHAR(36) NOT NULL,
  `nome` VARCHAR(45) NOT NULL,
  `nm_login` VARCHAR(45) NOT NULL,
  `senha` VARCHAR(45) NOT NULL,
  `email` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id_funcionario`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `lalumaredb`.`pedido`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `lalumaredb`.`pedido` (
  `id_pedido` VARCHAR(36) NOT NULL,
  `id_cliente` VARCHAR(36) NOT NULL,
  `id_funcionario` VARCHAR(36) NOT NULL,
  `numero` VARCHAR(45) NOT NULL,
  `valor` VARCHAR(45) NOT NULL,
  `status` VARCHAR(45) NOT NULL,
  `forma_pagamento` VARCHAR(45) NOT NULL,
  `forma_retirada` VARCHAR(45) NOT NULL,
  `data_hora_pedido` DATETIME NOT NULL,
  `data_hora_previsao` DATETIME NOT NULL,
  `soma_qtd_produto` INT NOT NULL,
  `adicionais` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_pedido`),
  INDEX `fk_pedido_cliente_idx` (`id_cliente` ASC) VISIBLE,
  INDEX `fk_pedido_funcionario1_idx` (`id_funcionario` ASC) VISIBLE,
  CONSTRAINT `fk_pedido_cliente`
    FOREIGN KEY (`id_cliente`)
    REFERENCES `lalumaredb`.`cliente` (`id_cliente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_pedido_funcionario1`
    FOREIGN KEY (`id_funcionario`)
    REFERENCES `lalumaredb`.`funcionario` (`id_funcionario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `lalumaredb`.`produto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `lalumaredb`.`produto` (
  `id_produto` VARCHAR(36) NOT NULL,
  `tipo_produto` VARCHAR(45) NOT NULL,
  `qtd_produto` VARCHAR(45) NOT NULL,
  `valor_produto` VARCHAR(45) NOT NULL,
  `un_medida_produto` VARCHAR(45) NOT NULL,
  `qtd_pedido` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id_produto`))
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

INSERT INTO funcionario (id_funcionario, nome, nm_login, senha, email) VALUES ('1', 'func', 'func', 'Func123!', 'func@email.com');
INSERT INTO produto (id_produto, tipo_produto, qtd_produto, valor_produto, un_medida_produto, qtd_pedido) VALUES
  ('1', 'Mousse Ninho', '1000', '0', 'g', '50'),
  ('2', 'Mousse Ovomaltine', '1000', '0', 'g', '50'),
  ('3', 'Mousse Limão', '1000', '0', 'g', '50'),
  ('4', 'Mousse Amendoim', '1000', '0', 'g', '50'),
  ('5', 'Mousse Morango', '1000', '0', 'g', '50'),
  ('6', 'Uva', '2000', '0', 'g', '20'),
  ('7', 'Banana', '2000', '0', 'g', '50'),
  ('8', 'Morango', '2000', '0', 'g', '20'),
  ('9', 'Kiwi', '1000', '0', 'g', '20'),
  ('10', 'Amendoim', '1000', '0', 'g', '20'),
  ('11', 'Granola Tradicional', '1000', '0', 'g', '50'),
  ('12', 'Leite Condensado', '2000', '0', 'g', '50'),
  ('13', 'Leite em Pó', '1000', '0', 'g', '20'),
  ('14', 'Mel', '1000', '0', 'g', '20'),
  ('15', 'Paçoca', '2000', '0', 'g', '50'),
  ('16', 'Castanha de Caju', '1000', '0', 'g', '50'),
  ('17', 'Cobertura Caramelo', '1000', '0', 'g', '30'),
  ('18', 'Cobertura Chocolate', '1000', '0', 'g', '30'),
  ('19', 'Cobertura Morango', '1000', '0', 'g', '30'),
  ('20', 'Bis', '2000', '2.0', 'g', '50'),
  ('21', 'Kit Kat', '1000', '2.5', 'g', '50'),
  ('22', 'Confete', '2000', '2.0', 'g', '50'),
  ('23', 'Nescau Ball', '2000', '2.0', 'g', '50'),
  ('24', 'Trento', '2000', '2.5', 'g', '50'),
  ('25', 'Açai-300', '10000', '18', 'ml', '300'),
  ('26', 'Açai-500', '10000', '20', 'ml', '500');
